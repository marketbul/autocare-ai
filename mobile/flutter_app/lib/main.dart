import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'theme/app_theme.dart';
import 'widgets/frosted_tab_bar.dart';
import 'screens/home_screen.dart';
import 'screens/diagnostic_screen.dart';
import 'screens/causal_graph_screen.dart';
import 'screens/pricing_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: AppColors.background,
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );
  runApp(const AutoCareApp());
}

class AutoCareApp extends StatelessWidget {
  const AutoCareApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AutoCare AI',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const MainNavigationShell(),
    );
  }
}

class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({Key? key}) : super(key: key);

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  int _currentIndex = 0;

  void _navigateToTab(int index) {
    setState(() => _currentIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      HomeScreen(
        onOpenAsk: () => _navigateToTab(0),
        onOpenGraph: () => _navigateToTab(1),
        onOpenQuotes: () => _navigateToTab(2),
      ),
      const CausalGraphScreen(),
      const PricingScreen(),
      const DiagnosticScreen(),
    ];

    return Scaffold(
      backgroundColor: AppColors.background,
      body: Stack(
        children: [
          IndexedStack(
            index: _currentIndex,
            children: screens,
          ),
          Positioned(
            left: 20,
            right: 20,
            bottom: 20,
            child: FrostedTabBar(
              currentIndex: _currentIndex,
              onTap: _navigateToTab,
            ),
          ),
        ],
      ),
    );
  }
}
