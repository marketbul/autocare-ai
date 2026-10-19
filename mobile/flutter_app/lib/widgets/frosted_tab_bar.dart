import 'dart:ui';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class FrostedTabBar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;

  const FrostedTabBar({
    Key? key,
    required this.currentIndex,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(32),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          height: 68,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: const Color(0xE618181B), // 90% opacity surface
            borderRadius: BorderRadius.circular(32),
            border: Border.all(color: const Color(0x24FFFFFF), width: 1),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.4),
                blurRadius: 24,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildTabItem(0, CupertinoIcons.gauge, 'Diagnostic'),
              _buildTabItem(1, CupertinoIcons.shuffle, 'Causal KG'),
              _buildTabItem(2, CupertinoIcons.wrench, 'PKR Quotes'),
              _buildTabItem(3, CupertinoIcons.car_detailed, 'Garage'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTabItem(int index, IconData icon, String label) {
    final bool isSelected = currentIndex == index;
    return GestureDetector(
      onTap: () => onTap(index),
      behavior: HitTestBehavior.opaque,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOutCubic,
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.electricViolet.withOpacity(0.15) : Colors.transparent,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 20,
              color: isSelected ? AppColors.electricViolet : AppColors.textMuted,
            ),
            const SizedBox(height: 3),
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                color: isSelected ? AppColors.electricViolet : AppColors.textMuted,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
