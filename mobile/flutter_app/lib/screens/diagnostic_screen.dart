import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class DiagnosticScreen extends StatefulWidget {
  const DiagnosticScreen({Key? key}) : super(key: key);

  @override
  State<DiagnosticScreen> createState() => _DiagnosticScreenState();
}

class _DiagnosticScreenState extends State<DiagnosticScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, dynamic>> _messages = [
    {
      'isUser': false,
      'text': 'Hello! I am your AutoCare AI diagnostic copilot. Describe your vehicle symptoms in English, Urdu, or Roman Urdu (e.g., "radiator fan not spinning in Lahore traffic" or "gaadi garam ho rahi hai").',
      'citation': null,
      'confidence': 1.0,
    },
  ];

  void _sendMessage() {
    final query = _controller.text.trim();
    if (query.isEmpty) return;

    setState(() {
      _messages.add({
        'isUser': true,
        'text': query,
        'citation': null,
        'confidence': 1.0,
      });
      _messages.add({
        'isUser': false,
        'text': 'Diagnostic Analysis for Toyota Corolla (2015-2025):\nBased on symptoms matching "engine overheating with AC on", the primary cause is a malfunctioning Radiator Fan Relay or low coolant volume.',
        'citation': 'Corolla 2018 Maintenance Manual, Sec 8.2 (Cooling Fan Circuit)',
        'confidence': 0.94,
        'cost_estimate': 'PKR 2,800 (Relay) + PKR 1,500 (Labour)',
      });
      _controller.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('AI Diagnostic Copilot'),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.electricViolet.withOpacity(0.12),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.electricViolet.withOpacity(0.3)),
            ),
            child: const Center(
              child: Text(
                'ECE: 0.042 (Platt)',
                style: TextStyle(color: AppColors.violetLight, fontSize: 11, fontWeight: FontWeight.w600),
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final m = _messages[index];
                final isUser = m['isUser'] as bool;
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(14),
                    constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.82),
                    decoration: BoxDecoration(
                      color: isUser ? AppColors.electricViolet : AppColors.card,
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(color: isUser ? Colors.transparent : AppColors.hairline),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          m['text'] as String,
                          style: TextStyle(
                            color: isUser ? Colors.white : AppColors.textPrimary,
                            fontSize: 13,
                            height: 1.4,
                          ),
                        ),
                        if (m['citation'] != null) ...[
                          const SizedBox(height: 8),
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: AppColors.background.withOpacity(0.6),
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: AppColors.emerald.withOpacity(0.3)),
                            ),
                            child: Row(
                              children: [
                                const Icon(CupertinoIcons.checkmark_seal_fill, color: AppColors.emerald, size: 14),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    m['citation'] as String,
                                    style: const TextStyle(color: AppColors.emeraldLight, fontSize: 10, fontWeight: FontWeight.w600),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              },
            ),
          ),

          // Chat Input Bar
          Container(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 90),
            decoration: const BoxDecoration(
              color: AppColors.surface,
              border: Border(top: BorderSide(color: AppColors.hairline)),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14),
                    decoration: BoxDecoration(
                      color: AppColors.card,
                      borderRadius: BorderRadius.circular(24),
                      border: Border.all(color: AppColors.hairline),
                    ),
                    child: TextField(
                      controller: _controller,
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                      decoration: const InputDecoration(
                        hintText: 'Describe car issue (Urdu/English)...',
                        hintStyle: TextStyle(color: AppColors.textMuted, fontSize: 12),
                        border: InputBorder.none,
                      ),
                      onSubmitted: (_) => _sendMessage(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: _sendMessage,
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: const BoxDecoration(
                      color: AppColors.electricViolet,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(CupertinoIcons.arrow_up, color: Colors.white, size: 16),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
