import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  final VoidCallback onOpenAsk;
  final VoidCallback onOpenGraph;
  final VoidCallback onOpenQuotes;

  const HomeScreen({
    Key? key,
    required this.onOpenAsk,
    required this.onOpenGraph,
    required this.onOpenQuotes,
  }) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _isLoading = false;
  Map<String, dynamic> _reliability = {};
  List<dynamic> _quotes = [];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final r = await ApiService.getModelReliability();
    final q = await ApiService.getPricingQuotes(model: 'corolla');
    if (mounted) {
      setState(() {
        _reliability = r;
        _quotes = q.take(2).toList();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        bottom: false,
        child: RefreshIndicator(
          color: AppColors.electricViolet,
          backgroundColor: AppColors.card,
          onRefresh: _loadData,
          child: CustomScrollView(
            physics: const BouncingScrollPhysics(parent: AlwaysScrollableScrollPhysics()),
            slivers: [
              // Top Bar
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Container(
                            height: 40,
                            width: 40,
                            decoration: BoxDecoration(
                              gradient: const LinearGradient(
                                colors: [Color(0xFF8B5CF6), Color(0xFF6366F1)],
                              ),
                              borderRadius: BorderRadius.circular(14),
                              boxShadow: [
                                BoxShadow(
                                  color: AppColors.electricViolet.withOpacity(0.3),
                                  blurRadius: 12,
                                  offset: const Offset(0, 4),
                                ),
                              ],
                            ),
                            child: const Icon(CupertinoIcons.bolt_fill, color: Colors.white, size: 20),
                          ),
                          const SizedBox(width: 12),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: const [
                              Text(
                                'AutoCare AI',
                                style: TextStyle(
                                  color: AppColors.textPrimary,
                                  fontSize: 16,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: -0.3,
                                ),
                              ),
                              Text(
                                'Corolla Altis Grande (2022)',
                                style: TextStyle(
                                  color: AppColors.textSecondary,
                                  fontSize: 12,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                        decoration: BoxDecoration(
                          color: AppColors.emerald.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: AppColors.emerald.withOpacity(0.3)),
                        ),
                        child: Row(
                          children: [
                            Container(
                              height: 6,
                              width: 6,
                              decoration: const BoxDecoration(
                                color: AppColors.emeraldLight,
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 6),
                            const Text(
                              'ECU Online',
                              style: TextStyle(
                                color: AppColors.emeraldLight,
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // Bento Cards Feed
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 110),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    // Card 1: Urgent Triage Alert Card
                    _buildUrgentTriageCard(),
                    const SizedBox(height: 16),

                    // Card 2: Directed Causal Knowledge Graph Card
                    _buildCausalGraphCard(),
                    const SizedBox(height: 16),

                    // Card 3: Subsystem Weibull Hazard Forecaster
                    _buildSubsystemHealthCard(),
                    const SizedBox(height: 16),

                    // Card 4: Pakistani Parts & Labour Rate Card (PKR)
                    _buildPricingQuotesCard(),
                  ]),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildUrgentTriageCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1B1115),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.rose.withOpacity(0.35)),
        boxShadow: [
          BoxShadow(
            color: AppColors.rose.withOpacity(0.08),
            blurRadius: 18,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: const [
                  Icon(CupertinoIcons.exclamationmark_triangle_fill, color: AppColors.rose, size: 16),
                  SizedBox(width: 6),
                  Text(
                    'CRITICAL SAFETY FAULT',
                    style: TextStyle(
                      color: AppColors.rose,
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.rose.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: const Text(
                  '10× Penalty Loss',
                  style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          const Text(
            'P0217 Engine Coolant Overheating',
            style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 6),
          const Text(
            'Multi-hop causal reasoning identified radiator fan relay failure. Stop vehicle safely within 3 km to prevent head gasket damage.',
            style: TextStyle(color: AppColors.textSecondary, fontSize: 12, height: 1.4),
          ),
          const SizedBox(height: 14),
          GestureDetector(
            onTap: widget.onOpenAsk,
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 10),
              decoration: BoxDecoration(
                color: AppColors.rose,
                borderRadius: BorderRadius.circular(14),
              ),
              alignment: Alignment.center,
              child: const Text(
                'Inspect Guided Resolution Steps',
                style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w700),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCausalGraphCard() {
    return GestureDetector(
      onTap: widget.onOpenGraph,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppColors.card,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: AppColors.hairline),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppColors.electricViolet.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(CupertinoIcons.shuffle, color: AppColors.electricViolet, size: 16),
                    ),
                    const SizedBox(width: 10),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: const [
                        Text(
                          'Causal Knowledge Graph (M6)',
                          style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w700),
                        ),
                        Text(
                          'Multi-Hop Root Cause Traversal',
                          style: TextStyle(color: AppColors.textMuted, fontSize: 11),
                        ),
                      ],
                    ),
                  ],
                ),
                const Icon(CupertinoIcons.chevron_forward, color: AppColors.textMuted, size: 18),
              ],
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.background.withOpacity(0.7),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppColors.borderSubtle),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildNodeStep('Coolant Boil', 'Symptom', AppColors.rose),
                  const Icon(CupertinoIcons.arrow_right, color: AppColors.textMuted, size: 14),
                  _buildNodeStep('Fan Stoppage', 'Failure Mode', AppColors.amber),
                  const Icon(CupertinoIcons.arrow_right, color: AppColors.textMuted, size: 14),
                  _buildNodeStep('Relay Welded', 'Root Cause', AppColors.electricViolet),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNodeStep(String title, String role, Color color) {
    return Column(
      children: [
        Text(role.toUpperCase(), style: TextStyle(color: color, fontSize: 9, fontWeight: FontWeight.w700)),
        const SizedBox(height: 2),
        Text(title, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w600)),
      ],
    );
  }

  Widget _buildSubsystemHealthCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.hairline),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: const [
              Text(
                'Weibull Hazard Health Radar (M8)',
                style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w700),
              ),
              Text(
                'β = 2.4 Wear-out',
                style: TextStyle(color: AppColors.electricViolet, fontSize: 11, fontWeight: FontWeight.w600),
              ),
            ],
          ),
          const SizedBox(height: 14),
          _buildHealthProgressBar('Braking Pads & Rotors', 0.78, AppColors.emeraldLight, '78% RUL'),
          const SizedBox(height: 10),
          _buildHealthProgressBar('Engine Cooling Circuit', 0.42, AppColors.amber, '42% Service Soon'),
          const SizedBox(height: 10),
          _buildHealthProgressBar('Transmission Gearbox ATF', 0.91, AppColors.electricViolet, '91% Optimal'),
        ],
      ),
    );
  }

  Widget _buildHealthProgressBar(String label, double val, Color color, String status) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(color: AppColors.textPrimary, fontSize: 11, fontWeight: FontWeight.w500)),
            Text(status, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: 5),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: val,
            minHeight: 5,
            backgroundColor: const Color(0xFF27272A),
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ),
      ],
    );
  }

  Widget _buildPricingQuotesCard() {
    return GestureDetector(
      onTap: widget.onOpenQuotes,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppColors.card,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: AppColors.hairline),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppColors.emerald.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(CupertinoIcons.money_dollar, color: AppColors.emerald, size: 16),
                    ),
                    const SizedBox(width: 10),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: const [
                        Text(
                          'Pakistan Parts & Labour (PKR)',
                          style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w700),
                        ),
                        Text(
                          'Bilal Gunj & Shershah Market Rates',
                          style: TextStyle(color: AppColors.textMuted, fontSize: 11),
                        ),
                      ],
                    ),
                  ],
                ),
                const Icon(CupertinoIcons.chevron_forward, color: AppColors.textMuted, size: 18),
              ],
            ),
            const SizedBox(height: 14),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: const [
                Text('Radiator Cooling Fan Motor', style: TextStyle(color: AppColors.textPrimary, fontSize: 12, fontWeight: FontWeight.w600)),
                Text('PKR 14,000', style: TextStyle(color: AppColors.emeraldLight, fontSize: 12, fontWeight: FontWeight.w700)),
              ],
            ),
            const Divider(color: AppColors.borderSubtle, height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: const [
                Text('Workshop Replacement Labour', style: TextStyle(color: AppColors.textPrimary, fontSize: 12, fontWeight: FontWeight.w600)),
                Text('PKR 2,500', style: TextStyle(color: AppColors.violetLight, fontSize: 12, fontWeight: FontWeight.w700)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
