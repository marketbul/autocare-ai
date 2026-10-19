import React, { useState } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  SafeAreaView,
  StatusBar,
} from "react-native";
import {
  Activity,
  AlertOctagon,
  Car,
  ChevronRight,
  GitBranch,
  ShieldCheck,
  Wrench,
  Zap,
} from "lucide-react-native";

export default function App() {
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState("diagnostic");

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1200);
  }, []);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#09090b" }}>
      <StatusBar barStyle="light-content" backgroundColor="#09090b" />

      {/* Top Header */}
      <View style={{
        paddingHorizontal: 20,
        paddingTop: 12,
        paddingBottom: 16,
        borderBottomWidth: 1,
        borderBottomColor: "rgba(255, 255, 255, 0.08)",
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "space-between"
      }}>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}>
          <View style={{
            height: 40,
            width: 40,
            borderRadius: 14,
            backgroundColor: "rgba(139, 92, 246, 0.15)",
            borderWidth: 1,
            borderColor: "rgba(139, 92, 246, 0.3)",
            alignItems: "center",
            justifyContent: "center"
          }}>
            <Zap size={20} color="#8b5cf6" />
          </View>
          <View>
            <Text style={{ fontSize: 16, fontWeight: "700", color: "#f4f4f5", letterSpacing: -0.3 }}>
              AutoCare AI
            </Text>
            <Text style={{ fontSize: 12, color: "#a1a1aa", fontWeight: "500" }}>
              Corolla Altis Grande (2022)
            </Text>
          </View>
        </View>

        <View style={{
          flexDirection: "row",
          alignItems: "center",
          gap: 6,
          backgroundColor: "rgba(16, 185, 129, 0.12)",
          borderWidth: 1,
          borderColor: "rgba(16, 185, 129, 0.3)",
          paddingHorizontal: 12,
          paddingVertical: 5,
          borderRadius: 20
        }}>
          <View style={{ height: 6, width: 6, borderRadius: 3, backgroundColor: "#34d399" }} />
          <Text style={{ fontSize: 11, fontWeight: "700", color: "#34d399" }}>
            ECU Online
          </Text>
        </View>
      </View>

      {/* Main Bento Cards Feed */}
      <ScrollView
        style={{ flex: 1, paddingHorizontal: 20, paddingTop: 16 }}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor="#8b5cf6"
          />
        }
      >
        {/* Card 1: Critical Safety Triage Card */}
        <View style={{
          borderRadius: 24,
          borderWidth: 1,
          borderColor: "rgba(244, 63, 94, 0.35)",
          backgroundColor: "rgba(244, 63, 94, 0.08)",
          padding: 20,
          marginBottom: 16
        }}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
              <AlertOctagon size={16} color="#f43f5e" />
              <Text style={{ fontSize: 11, fontWeight: "700", color: "#f43f5e", letterSpacing: 0.5 }}>
                CRITICAL SAFETY FAULT (M2)
              </Text>
            </View>
            <View style={{ backgroundColor: "rgba(244, 63, 94, 0.2)", paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 }}>
              <Text style={{ color: "#fff", fontSize: 10, fontWeight: "700" }}>10× Safety Matrix</Text>
            </View>
          </View>

          <Text style={{ fontSize: 17, fontWeight: "700", color: "#ffffff", letterSpacing: -0.2 }}>
            P0217 Engine Coolant Overheating
          </Text>
          <Text style={{ fontSize: 12, color: "#cbd5e1", marginTop: 4, lineHeight: 18 }}>
            Directed causal inference identified radiator fan relay contacts stuck. Stop vehicle safely within 3 km to prevent head gasket breach.
          </Text>

          <TouchableOpacity style={{
            marginTop: 14,
            backgroundColor: "#f43f5e",
            borderRadius: 14,
            paddingVertical: 10,
            alignItems: "center"
          }}>
            <Text style={{ fontSize: 13, fontWeight: "700", color: "#ffffff" }}>
              Inspect Guided Resolution Steps
            </Text>
          </TouchableOpacity>
        </View>

        {/* Card 2: Causal Knowledge Graph Card */}
        <View style={{
          borderRadius: 24,
          borderWidth: 1,
          borderColor: "rgba(255, 255, 255, 0.08)",
          backgroundColor: "#18181b",
          padding: 20,
          marginBottom: 16
        }}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 10 }}>
              <View style={{
                padding: 8,
                borderRadius: 10,
                backgroundColor: "rgba(139, 92, 246, 0.12)",
                borderWidth: 1,
                borderColor: "rgba(139, 92, 246, 0.3)"
              }}>
                <GitBranch size={16} color="#8b5cf6" />
              </View>
              <View>
                <Text style={{ fontSize: 14, fontWeight: "700", color: "#ffffff" }}>
                  Causal Knowledge Graph (M6)
                </Text>
                <Text style={{ fontSize: 11, color: "#71717a" }}>
                  Multi-Hop Directed Causal Inference
                </Text>
              </View>
            </View>
            <ChevronRight size={18} color="#71717a" />
          </View>

          <View style={{
            backgroundColor: "rgba(9, 9, 11, 0.7)",
            borderRadius: 14,
            borderWidth: 1,
            borderColor: "rgba(255, 255, 255, 0.05)",
            padding: 12,
            flexDirection: "row",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
            <View style={{ alignItems: "center" }}>
              <Text style={{ color: "#f43f5e", fontSize: 9, fontWeight: "700" }}>SYMPTOM</Text>
              <Text style={{ color: "#ffffff", fontSize: 11, fontWeight: "600", marginTop: 2 }}>Coolant Boil</Text>
            </View>
            <Text style={{ color: "#71717a", fontSize: 12 }}>→</Text>
            <View style={{ alignItems: "center" }}>
              <Text style={{ color: "#f59e0b", fontSize: 9, fontWeight: "700" }}>FAILURE</Text>
              <Text style={{ color: "#ffffff", fontSize: 11, fontWeight: "600", marginTop: 2 }}>Fan Stoppage</Text>
            </View>
            <Text style={{ color: "#71717a", fontSize: 12 }}>→</Text>
            <View style={{ alignItems: "center" }}>
              <Text style={{ color: "#8b5cf6", fontSize: 9, fontWeight: "700" }}>ROOT CAUSE</Text>
              <Text style={{ color: "#ffffff", fontSize: 11, fontWeight: "600", marginTop: 2 }}>Relay Welded</Text>
            </View>
          </View>
        </View>

        {/* Card 3: Subsystem Health & Hazard Forecaster */}
        <View style={{
          borderRadius: 24,
          borderWidth: 1,
          borderColor: "rgba(255, 255, 255, 0.08)",
          backgroundColor: "#18181b",
          padding: 20,
          marginBottom: 16
        }}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
            <Text style={{ fontSize: 14, fontWeight: "700", color: "#ffffff" }}>
              Weibull Degradation Radar (M8)
            </Text>
            <Text style={{ fontSize: 11, fontWeight: "700", color: "#8b5cf6" }}>
              β = 2.4 Wear-out
            </Text>
          </View>

          {[
            { label: "Braking System", val: "78% RUL", color: "#34d399", pct: "78%" },
            { label: "Cooling Circuit", val: "42% Service Soon", color: "#f59e0b", pct: "42%" },
            { label: "Transmission & Gearbox", val: "91% Optimal", color: "#8b5cf6", pct: "91%" },
          ].map((sub, i) => (
            <View key={i} style={{ marginBottom: 10 }}>
              <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 4 }}>
                <Text style={{ fontSize: 11, color: "#f4f4f5", fontWeight: "500" }}>{sub.label}</Text>
                <Text style={{ fontSize: 11, color: sub.color, fontWeight: "700" }}>{sub.val}</Text>
              </View>
              <View style={{ height: 5, backgroundColor: "#27272a", borderRadius: 3, overflow: "hidden" }}>
                <View style={{ height: "100%", width: sub.pct as any, backgroundColor: sub.color, borderRadius: 3 }} />
              </View>
            </View>
          ))}
        </View>

        {/* Card 4: Pakistan Parts & Labour Rates in PKR */}
        <View style={{
          borderRadius: 24,
          borderWidth: 1,
          borderColor: "rgba(255, 255, 255, 0.08)",
          backgroundColor: "#18181b",
          padding: 20,
          marginBottom: 100
        }}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <Text style={{ fontSize: 14, fontWeight: "700", color: "#ffffff" }}>
              Pakistan Parts & Labour (PKR)
            </Text>
            <Text style={{ fontSize: 11, color: "#34d399", fontWeight: "700" }}>
              Bilal Gunj Verified
            </Text>
          </View>

          <View style={{ flexDirection: "row", justifyContent: "space-between", paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: "rgba(255,255,255,0.04)" }}>
            <Text style={{ fontSize: 12, color: "#cbd5e1" }}>Radiator Cooling Fan Motor</Text>
            <Text style={{ fontSize: 12, fontWeight: "700", color: "#34d399" }}>PKR 14,000</Text>
          </View>
          <View style={{ flexDirection: "row", justifyContent: "space-between", paddingVertical: 6 }}>
            <Text style={{ fontSize: 12, color: "#cbd5e1" }}>Workshop Replacement Labour</Text>
            <Text style={{ fontSize: 12, fontWeight: "700", color: "#a78bfa" }}>PKR 2,500</Text>
          </View>
        </View>
      </ScrollView>

      {/* Floating Bottom Frosted Tab Bar */}
      <View style={{
        position: "absolute",
        bottom: 20,
        left: 20,
        right: 20,
        height: 64,
        borderRadius: 32,
        backgroundColor: "rgba(24, 24, 27, 0.92)",
        borderWidth: 1,
        borderColor: "rgba(255, 255, 255, 0.12)",
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "space-around",
        paddingHorizontal: 12,
        elevation: 12
      }}>
        {[
          { id: "diagnostic", label: "Diagnostic", icon: Activity },
          { id: "graph", label: "Causal KG", icon: GitBranch },
          { id: "pricing", label: "PKR Rates", icon: Wrench },
          { id: "garage", label: "My Cars", icon: Car },
        ].map((tab) => {
          const Icon = tab.icon;
          const isSelected = activeTab === tab.id;
          return (
            <TouchableOpacity
              key={tab.id}
              onPress={() => setActiveTab(tab.id)}
              style={{
                alignItems: "center",
                justifyContent: "center",
                paddingVertical: 6,
                paddingHorizontal: 12,
                borderRadius: 18,
                backgroundColor: isSelected ? "rgba(139, 92, 246, 0.18)" : "transparent"
              }}
            >
              <Icon size={18} color={isSelected ? "#8b5cf6" : "#71717a"} />
              <Text style={{
                fontSize: 10,
                marginTop: 2,
                fontWeight: isSelected ? "700" : "500",
                color: isSelected ? "#8b5cf6" : "#71717a"
              }}>
                {tab.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </SafeAreaView>
  );
}
