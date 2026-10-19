import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Configured for local FastAPI backend
  // Use 10.0.2.2 for Android Emulator, 127.0.0.1 for iOS simulator / desktop
  static const String baseUrl = 'http://127.0.0.1:8000';

  static Future<Map<String, dynamic>> checkHealth() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/v1/health'));
      if (res.statusCode == 200) {
        return json.decode(res.body);
      }
    } catch (_) {}
    return {'status': 'offline'};
  }

  static Future<Map<String, dynamic>> getModelReliability() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/v1/analytics/model-reliability'));
      if (res.statusCode == 200) {
        return json.decode(res.body);
      }
    } catch (_) {}
    return {};
  }

  static Future<List<dynamic>> getPricingQuotes({String model = 'corolla', String category = 'all'}) async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/v1/pricing/quotes?model=$model&category=$category'));
      if (res.statusCode == 200) {
        return json.decode(res.body);
      }
    } catch (_) {}
    return [];
  }

  static Future<Map<String, dynamic>> getKnowledgeGraph() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/v1/diagnose/graph/export'));
      if (res.statusCode == 200) {
        return json.decode(res.body);
      }
    } catch (_) {}
    return {};
  }
}
