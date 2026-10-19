import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/api_service.dart';

class PricingScreen extends StatefulWidget {
  const PricingScreen({Key? key}) : super(key: key);

  @override
  State<PricingScreen> createState() => _PricingScreenState();
}

class _PricingScreenState extends State<PricingScreen> {
  String _selectedVehicle = 'corolla';
  String _selectedCategory = 'all';
  bool _loading = false;
  List<dynamic> _quotes = [];

  @override
  void initState() {
    super.initState();
    _fetchQuotes();
  }

  Future<void> _fetchQuotes() async {
    setState(() => _loading = true);
    final data = await ApiService.getPricingQuotes(model: _selectedVehicle, category: _selectedCategory);
    if (mounted) {
      setState(() {
        _quotes = data.isNotEmpty
            ? data
            : [
                {
                  'part_name': 'Front Brake Pads (Set)',
                  'category': 'braking',
                  'oem_price_range_pkr': 'PKR 14,500 - 18,000',
                  'aftermarket_price_range_pkr': 'PKR 6,500 - 9,000',
                  'labor_estimate_pkr': 'PKR 1,500',
                },
                {
                  'part_name': 'Radiator Cooling Fan Motor',
                  'category': 'cooling',
                  'oem_price_range_pkr': 'PKR 26,000 - 32,000',
                  'aftermarket_price_range_pkr': 'PKR 13,000 - 16,500',
                  'labor_estimate_pkr': 'PKR 2,500',
                },
                {
                  'part_name': 'Synthetic Engine Oil (0W-20 4L)',
                  'category': 'engine',
                  'oem_price_range_pkr': 'PKR 12,500 - 14,000',
                  'aftermarket_price_range_pkr': 'PKR 8,500 - 10,500',
                  'labor_estimate_pkr': 'PKR 800',
                },
              ];
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Pakistan Parts & Labour (PKR)'),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.emerald.withOpacity(0.12),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.emerald.withOpacity(0.3)),
            ),
            child: const Center(
              child: Text(
                'Proposal §7.9',
                style: TextStyle(color: AppColors.emeraldLight, fontSize: 10, fontWeight: FontWeight.w700),
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // Vehicle Model Selector
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
            child: Row(
              children: [
                _buildVehicleChip('corolla', 'Toyota Corolla'),
                const SizedBox(width: 8),
                _buildVehicleChip('civic', 'Honda Civic'),
                const SizedBox(width: 8),
                _buildVehicleChip('swift', 'Suzuki Swift'),
              ],
            ),
          ),

          // Quotes List
          Expanded(
            child: _loading
                ? const Center(child: CupertinoActivityIndicator(color: AppColors.electricViolet))
                : ListView.builder(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 90),
                    itemCount: _quotes.length,
                    itemBuilder: (context, index) {
                      final q = _quotes[index];
                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AppColors.card,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: AppColors.hairline),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  q['part_name'] ?? '',
                                  style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w700),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: AppColors.electricViolet.withOpacity(0.12),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    (q['category'] ?? 'part').toString().toUpperCase(),
                                    style: const TextStyle(color: AppColors.violetLight, fontSize: 9, fontWeight: FontWeight.w700),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            _buildPriceRow('Genuine OEM Range', q['oem_price_range_pkr'] ?? '', AppColors.violetLight),
                            const SizedBox(height: 6),
                            _buildPriceRow('Quality Aftermarket', q['aftermarket_price_range_pkr'] ?? '', AppColors.emeraldLight),
                            const SizedBox(height: 6),
                            _buildPriceRow('Standard Labour Fee', q['labor_estimate_pkr'] ?? '', AppColors.textSecondary),
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

  Widget _buildVehicleChip(String id, String label) {
    final isSelected = _selectedVehicle == id;
    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() => _selectedVehicle = id);
          _fetchQuotes();
        },
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.electricViolet : AppColors.card,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: isSelected ? Colors.transparent : AppColors.hairline),
          ),
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              color: isSelected ? Colors.white : AppColors.textMuted,
              fontSize: 10,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPriceRow(String label, String value, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: AppColors.textMuted, fontSize: 11)),
        Text(value, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w700)),
      ],
    );
  }
}
