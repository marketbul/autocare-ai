"""M6: Automotive Knowledge Graph and Multi-Hop Root-Cause Inference.

Nodes: components, symptoms, diagnostic codes, fluids, service actions.
Edges: causes, indicates, depends_on, addressed_by, co_occurs_with.

Provides:
- Multi-hop causal chain inference: symptom <- intermediate fault <- root cause.
- Structural verification: checks if a proposed repair component has a causal path to observed symptoms.
- Graph-informed query expansion: expands retrieval query with causally adjacent components.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import networkx as nx


@dataclass
class CausalStep:
    from_node: str
    from_label: str
    relation: str
    to_node: str
    to_label: str
    confidence: float
    evidence_chunk_id: str | None = None


@dataclass
class CausalChain:
    symptom: str
    root_cause: str
    steps: list[CausalStep] = field(default_factory=list)
    total_confidence: float = 1.0

    @property
    def readable_chain(self) -> str:
        if not self.steps:
            return self.symptom
        nodes = [self.steps[0].to_label]
        for s in reversed(self.steps):
            nodes.append(s.from_label)
        return " <- ".join(nodes)


class AutomotiveKnowledgeGraph:
    def __init__(self, db=None):
        self.db = db
        self.g = nx.DiGraph()
        self.node_metadata: dict[str, dict] = {}
        if db is not None:
            self.load_from_db()

    def add_node(self, node_id: str, node_type: str, canonical_name: str,
                 aliases: list[str] | None = None, vehicle_scope: list[str] | None = None) -> None:
        nid = node_id.strip().lower()
        self.g.add_node(nid, node_type=node_type, canonical_name=canonical_name)
        self.node_metadata[nid] = {
            "node_type": node_type,
            "canonical_name": canonical_name,
            "aliases": [a.lower() for a in (aliases or [])],
            "vehicle_scope": vehicle_scope,
        }

    def add_edge(self, source_node: str, target_node: str, relation_type: str,
                 confidence: float = 1.0, evidence_chunk_id: str | None = None) -> None:
        src = source_node.strip().lower()
        tgt = target_node.strip().lower()
        self.g.add_edge(src, tgt, relation_type=relation_type,
                        confidence=confidence, evidence_chunk_id=evidence_chunk_id)

    def load_from_db(self) -> None:
        nodes = self.db.query("SELECT node_id, node_type, canonical_name, aliases, vehicle_scope FROM graphnode")
        for n in nodes:
            aliases = json.loads(n["aliases"]) if n.get("aliases") else []
            scope = json.loads(n["vehicle_scope"]) if n.get("vehicle_scope") else None
            self.add_node(n["node_id"], n["node_type"], n["canonical_name"], aliases, scope)

        edges = self.db.query("""SELECT source_node, target_node, relation_type, confidence, evidence_chunk_id
                                 FROM graphedge WHERE review_status = 'reviewed'""")
        for e in edges:
            self.add_edge(e["source_node"], e["target_node"], e["relation_type"],
                          float(e["confidence"] or 1.0), e.get("evidence_chunk_id"))

    def match_node(self, text: str) -> str | None:
        """Finds the best matching node ID from free text or keywords."""
        q = text.strip().lower()
        if q in self.g:
            return q
        for nid, meta in self.node_metadata.items():
            if meta["canonical_name"].lower() in q or q in meta["canonical_name"].lower():
                return nid
            for alias in meta["aliases"]:
                if alias in q:
                    return nid
        return None

    def find_root_causes(self, symptom_text: str, max_depth: int = 3) -> list[CausalChain]:
        """Given a symptom, traverse backwards along incoming 'causes' or 'indicates' edges

        to discover candidate root cause chains.
        """
        node = self.match_node(symptom_text)
        if not node or node not in self.g:
            return []

        chains: list[CausalChain] = []

        # Find paths where cause -> ... -> symptom
        for source in self.g.nodes:
            if source == node:
                continue
            if nx.has_path(self.g, source, node):
                for path in nx.all_simple_paths(self.g, source, node, cutoff=max_depth):
                    steps = []
                    valid_causal = True
                    prob = 1.0
                    for i in range(len(path) - 1):
                        u, v = path[i], path[i + 1]
                        edge_data = self.g.get_edge_data(u, v) or {}
                        rel = edge_data.get("relation_type", "causes")
                        if rel not in ("causes", "indicates", "depends_on"):
                            valid_causal = False
                            break
                        conf = float(edge_data.get("confidence", 1.0))
                        prob *= conf
                        steps.append(CausalStep(
                            from_node=u,
                            from_label=self.node_metadata.get(u, {}).get("canonical_name", u),
                            relation=rel,
                            to_node=v,
                            to_label=self.node_metadata.get(v, {}).get("canonical_name", v),
                            confidence=conf,
                            evidence_chunk_id=edge_data.get("evidence_chunk_id"),
                        ))
                    if valid_causal and steps:
                        chains.append(CausalChain(
                            symptom=self.node_metadata.get(node, {}).get("canonical_name", node),
                            root_cause=self.node_metadata.get(source, {}).get("canonical_name", source),
                            steps=steps,
                            total_confidence=prob,
                        ))

        # Sort by total confidence descending, then shorter chain
        chains.sort(key=lambda c: (-c.total_confidence, len(c.steps)))
        return chains[:5]

    def has_causal_path(self, proposed_component: str, symptom: str, max_hops: int = 3) -> tuple[bool, list[str]]:
        """Used by M5 Repair Verifier: checks if the proposed repair component

        has a documented causal path to the reported symptom within max_hops.
        """
        src = self.match_node(proposed_component)
        tgt = self.match_node(symptom)

        if not src or not tgt or src not in self.g or tgt not in self.g:
            return False, []

        if src == tgt:
            return True, [self.node_metadata.get(src, {}).get("canonical_name", src)]

        if nx.has_path(self.g, src, tgt):
            try:
                shortest = nx.shortest_path(self.g, src, tgt)
                if len(shortest) - 1 <= max_hops:
                    names = [self.node_metadata.get(n, {}).get("canonical_name", n) for n in shortest]
                    return True, names
            except nx.NetworkXNoPath:
                pass
        return False, []

    def get_related_components(self, text: str, max_count: int = 4) -> list[str]:
        """Graph-informed query expansion: returns names of adjacent components."""
        node = self.match_node(text)
        if not node or node not in self.g:
            return []

        neighbors = set()
        # predecessors (causes) and successors (effects)
        for p in self.g.predecessors(node):
            if self.node_metadata.get(p, {}).get("node_type") == "component":
                neighbors.add(self.node_metadata[p]["canonical_name"])
        for s in self.g.successors(node):
            if self.node_metadata.get(s, {}).get("node_type") == "component":
                neighbors.add(self.node_metadata[s]["canonical_name"])

        return list(neighbors)[:max_count]
