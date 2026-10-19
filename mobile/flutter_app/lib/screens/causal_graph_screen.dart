import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';

class CausalGraphScreen extends StatefulWidget {
  const CausalGraphScreen({Key? key}) : super(key: key);

  @override
  State<CausalGraphScreen> createState() => _CausalGraphScreenState();
}

class _CausalGraphScreenState extends State<CausalGraphScreen> {
  bool _loading = true;
  int _nodeCount = 49;
  int _edgeCount = 36;
  String _filter = 'all';

  final List<Map<String, String>> _sampleNodes = [
    {'name': 'engine_overheating', 'type': 'symptom', 'hops': 'Observed', 'desc': 'Coolant temp exceeds 105°C'},
    {'name': 'radiator_fan_stoppage', 'type': 'failure_mode', 'hops': '1 Hop', 'desc': 'Cooling fan motor unresponsive'},
    {'name': 'fan_relay_stuck', 'type': 'root_cause', 'hops': '2 Hops', 'desc': 'Contacts oxidized in fuse box'},
    {'name': 'thermostat_stuck_closed', 'type': 'root_cause', 'hops': '1 Hop', 'desc': 'Wax pellet expansion failure'},
    {'name': 'head_gasket_breach', 'type': 'failure_mode', 'hops': '2 Hops', 'desc': 'Combustion gas enters water jacket'},
    {'name': 'P0217', 'type': 'dtc', 'hops': 'ECU Code', 'desc': 'Engine Coolant Overtemperature Condition'},
  ];

  @override
  void initState() {
    super.initState();
    _fetchGraph();
  }

  Future<void> _fetchGraph() async {
    final data = await ApiService.getKnowledgeGraph();
    if (mounted) {
      setState(() {
        if (data.containsKey('stats')) {
          _nodeCount = data['stats']['total_nodes'] ?? 49;
          _edgeCount = data['stats']['total_edges'] ?? 36;
        }
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Causal Knowledge Graph'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(
              child: Text(
                '$_nodeCount Nodes • $_edgeCount Edges',
                style: const TextStyle(color: AppColors.violetLight, fontSize: 11, fontWeight: FontWeight.w600),
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: ['all', 'symptom', 'failure_mode', 'root_cause', 'dtc'].map((f) {
                final isSelected = _filter == f;
                return GestureDetector(
                  onTap: () => setState(() => _filter = f),
                  child: Container(
                    margin: const EdgeInsets.only(right: 8),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                    decoration: BoxDecoration(
                      color: isSelected ? AppColors.electricViolet.withOpacity(0.2) : AppColors.card,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: isSelected ? AppColors.electricViolet : AppColors.hairline,
                      ),
                    ),
                    child: Text(
                      f.toUpperCase(),
                      style: TextStyle(
                        color: isSelected ? Colors.white : AppColors.textMuted,
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),

          // Node List
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 90),
              itemCount: _sampleNodes.length,
              itemBuilder: (context, index) {
                final node = _sampleNodes[index];
                if (_filter != 'all' && node['type'] != _filter) return const SizedBox.shrink();

                Color badgeColor = AppColors.electricViolet;
                if (node['type'] == 'symptom') badgeColor = AppColors.rose;
                if (node['type'] == 'failure_mode') badgeColor = AppColors.amber;
                if (node['type'] == 'root_cause') badgeColor = AppColors.emerald;

                return Container(
                  margin: const EdgeInsets.only(bottom: 10),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppColors.card,
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(color: AppColors.hairline),
                  ),
                  child: Row(
                    children: [
                      Container(
                        height: 38,
                        width: 38,
                        decoration: BoxDecoration(
                          color: badgeColor.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: badgeColor.withOpacity(0.3)),
                        ),
                        child: Icon(CupertinoIcons.circle_grid_hex_fill, color: badgeColor, size: 18),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  node['name']!,
                                  style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w700),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: badgeColor.withOpacity(0.12),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    node['hops']!,
                                    style: TextStyle(color: badgeColor, fontSize: 9, fontWeight: FontWeight.w700),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              node['desc']!,
                              style: const TextStyle(color: AppColors.textSecondary, fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
