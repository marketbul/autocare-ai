import 'package:flutter/material.dart';

class AppColors {
  // Deep Slate / Zinc OLED Palette (Benchmarks: Linear, Raycast, Apple iOS)
  static const Color background = Color(0xFF09090B);
  static const Color surface = Color(0xFF121215);
  static const Color card = Color(0xFF18181B);
  static const Color elevated = Color(0xFF222227);
  static const Color hairline = Color(0x14FFFFFF); // rgba(255, 255, 255, 0.08)
  static const Color borderSubtle = Color(0x0FFFFFFF);

  // Typography
  static const Color textPrimary = Color(0xFFF4F4F5);
  static const Color textSecondary = Color(0xFFA1A1AA);
  static const Color textMuted = Color(0xFF71717A);

  // Brand & Functional Accents
  static const Color electricViolet = Color(0xFF8B5CF6);
  static const Color violetLight = Color(0xFFA78BFA);
  static const Color emerald = Color(0xFF10B981);
  static const Color emeraldLight = Color(0xFF34D399);
  static const Color rose = Color(0xFFF43F5E);
  static const Color amber = Color(0xFFF59E0B);
}

class AppTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: AppColors.background,
      primaryColor: AppColors.electricViolet,
      cardColor: AppColors.card,
      dividerColor: AppColors.hairline,
      fontFamily: 'Inter',
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: AppColors.textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w700,
          letterSpacing: -0.3,
        ),
      ),
      colorScheme: const ColorScheme.dark(
        primary: AppColors.electricViolet,
        secondary: AppColors.emerald,
        surface: AppColors.surface,
        error: AppColors.rose,
      ),
    );
  }
}
