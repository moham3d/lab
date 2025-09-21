#!/usr/bin/env python3
"""
Manual Code Analysis and Report Generator for Patient Visit Management System
Healthcare API Analysis and Documentation Generation - No Runtime Dependencies
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class ManualCodeAnalyzer:
    def __init__(self):
        self.project_root = Path("/home/runner/work/lab/lab")
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "project_name": "Patient Visit Management System",
            "analysis_type": "Comprehensive Healthcare API Analysis",
            "executive_summary": {},
            "architecture_analysis": {},
            "security_analysis": {},
            "healthcare_compliance": {},
            "api_endpoints": {},
            "database_design": {},
            "test_coverage": {},
            "performance_considerations": {},
            "recommendations": [],
            "critical_findings": []
        }
    
    def analyze_project_structure(self):
        """Analyze the project file structure and architecture"""
        print("📁 Analyzing project structure...")
        
        structure = {
            "total_files": 0,
            "python_files": 0,
            "directories": {},
            "key_components": {}
        }
        
        # Analyze directory structure
        for root, dirs, files in os.walk(self.project_root):
            if ".git" in root or "__pycache__" in root:
                continue
                
            rel_path = os.path.relpath(root, self.project_root)
            structure["directories"][rel_path] = {
                "files": [f for f in files if f.endswith('.py')],
                "total_files": len(files),
                "python_files": len([f for f in files if f.endswith('.py')])
            }
            
            structure["total_files"] += len(files)
            structure["python_files"] += len([f for f in files if f.endswith('.py')])
        
        # Identify key components
        key_paths = [
            "app/main.py",
            "app/database.py", 
            "app/core/config.py",
            "app/core/security.py",
            "requirements.txt",
            "docker-compose.yml",
            "README.md"
        ]
        
        for path in key_paths:
            full_path = self.project_root / path
            structure["key_components"][path] = {
                "exists": full_path.exists(),
                "size": full_path.stat().st_size if full_path.exists() else 0
            }
        
        self.analysis_results["architecture_analysis"]["structure"] = structure
        print(f"   ✅ Found {structure['python_files']} Python files in {len(structure['directories'])} directories")
    
    def analyze_api_endpoints(self):
        """Analyze API endpoints and their structure"""
        print("🔗 Analyzing API endpoints...")
        
        endpoints = {
            "authentication": [],
            "patients": [],
            "visits": [], 
            "assessments": [],
            "documents": [],
            "reports": [],
            "admin": []
        }
        
        # Read API endpoint files
        api_dir = self.project_root / "app" / "api" / "v1" / "endpoints"
        if api_dir.exists():
            for file_path in api_dir.glob("*.py"):
                if file_path.name == "__init__.py":
                    continue
                    
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Extract route definitions
                    route_pattern = r'@router\.(get|post|put|delete)\(["\']([^"\']+)["\']'
                    routes = re.findall(route_pattern, content)
                    
                    category = file_path.stem
                    if category in endpoints:
                        endpoints[category] = [
                            {"method": method.upper(), "path": path} 
                            for method, path in routes
                        ]
                    
                except Exception as e:
                    print(f"   ⚠️  Error reading {file_path}: {e}")
        
        self.analysis_results["api_endpoints"] = endpoints
        
        total_endpoints = sum(len(routes) for routes in endpoints.values())
        print(f"   ✅ Found {total_endpoints} API endpoints across {len(endpoints)} categories")
    
    def analyze_database_models(self):
        """Analyze database models and relationships"""
        print("🗄️  Analyzing database models...")
        
        models = {}
        models_dir = self.project_root / "app" / "models"
        
        if models_dir.exists():
            for file_path in models_dir.glob("*.py"):
                if file_path.name == "__init__.py":
                    continue
                    
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Extract model classes
                    class_pattern = r'class\s+(\w+)\([^)]*Base[^)]*\):'
                    classes = re.findall(class_pattern, content)
                    
                    # Extract fields
                    field_pattern = r'(\w+)\s*=\s*Column\('
                    fields = re.findall(field_pattern, content)
                    
                    # Extract relationships
                    rel_pattern = r'(\w+)\s*=\s*relationship\('
                    relationships = re.findall(rel_pattern, content)
                    
                    models[file_path.stem] = {
                        "classes": classes,
                        "fields": fields,
                        "relationships": relationships,
                        "file_size": file_path.stat().st_size
                    }
                    
                except Exception as e:
                    print(f"   ⚠️  Error reading {file_path}: {e}")
        
        self.analysis_results["database_design"]["models"] = models
        
        total_models = sum(len(info["classes"]) for info in models.values())
        total_fields = sum(len(info["fields"]) for info in models.values())
        print(f"   ✅ Found {total_models} models with {total_fields} total fields")
    
    def analyze_security_implementation(self):
        """Analyze security measures and HIPAA compliance"""
        print("🔒 Analyzing security implementation...")
        
        security_analysis = {
            "authentication": False,
            "authorization": False,
            "encryption": False,
            "audit_logging": False,
            "input_validation": False,
            "rate_limiting": False,
            "cors_configured": False,
            "security_headers": False
        }
        
        # Check security implementation files
        security_files = [
            "app/core/security.py",
            "app/core/security_middleware.py",
            "app/services/audit_service.py"
        ]
        
        for file_path in security_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    
                    # Check for various security features
                    if "JWT" in content or "token" in content.lower():
                        security_analysis["authentication"] = True
                    
                    if "role" in content.lower() or "permission" in content.lower():
                        security_analysis["authorization"] = True
                    
                    if "encrypt" in content.lower() or "hash" in content.lower():
                        security_analysis["encryption"] = True
                    
                    if "audit" in content.lower() or "log" in content.lower():
                        security_analysis["audit_logging"] = True
                    
                    if "validate" in content.lower() or "sanitize" in content.lower():
                        security_analysis["input_validation"] = True
                    
                    if "rate" in content.lower() and "limit" in content.lower():
                        security_analysis["rate_limiting"] = True
                    
                    if "cors" in content.lower():
                        security_analysis["cors_configured"] = True
                    
                    if "header" in content.lower() and "security" in content.lower():
                        security_analysis["security_headers"] = True
                        
                except Exception as e:
                    print(f"   ⚠️  Error reading {file_path}: {e}")
        
        self.analysis_results["security_analysis"] = security_analysis
        
        implemented_features = sum(security_analysis.values())
        print(f"   ✅ Found {implemented_features}/8 security features implemented")
    
    def analyze_healthcare_compliance(self):
        """Analyze HIPAA and healthcare-specific compliance measures"""
        print("🏥 Analyzing healthcare compliance...")
        
        compliance = {
            "phi_protection": False,
            "audit_trails": False,
            "data_encryption": False,
            "access_controls": False,
            "data_retention": False,
            "breach_detection": False,
            "egyptian_standards": False
        }
        
        # Check for healthcare-specific implementations
        healthcare_patterns = {
            "phi_protection": [r"phi", r"patient.*data", r"health.*information"],
            "audit_trails": [r"audit", r"log.*action", r"track.*access"],
            "data_encryption": [r"encrypt", r"hash", r"secure.*storage"],
            "access_controls": [r"role.*based", r"permission", r"authorize"],
            "data_retention": [r"retention", r"archive", r"delete.*policy"],
            "breach_detection": [r"breach", r"intrusion", r"security.*monitor"],
            "egyptian_standards": [r"egypt", r"14.*digit", r"01[0-2]", r"ssn.*format"]
        }
        
        # Search through all Python files
        for root, dirs, files in os.walk(self.project_root / "app"):
            if "__pycache__" in root:
                continue
                
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                file_path = Path(root) / file
                try:
                    content = file_path.read_text(encoding='utf-8').lower()
                    
                    for feature, patterns in healthcare_patterns.items():
                        if any(re.search(pattern, content) for pattern in patterns):
                            compliance[feature] = True
                            
                except Exception:
                    continue
        
        self.analysis_results["healthcare_compliance"] = compliance
        
        compliant_features = sum(compliance.values())
        print(f"   ✅ Found {compliant_features}/7 healthcare compliance features")
    
    def analyze_test_coverage(self):
        """Analyze test coverage and quality"""
        print("🧪 Analyzing test coverage...")
        
        test_analysis = {
            "total_test_files": 0,
            "contract_tests": 0,
            "unit_tests": 0,
            "integration_tests": 0,
            "test_categories": []
        }
        
        # Analyze test directory
        test_dir = self.project_root / "app" / "tests"
        if test_dir.exists():
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.startswith("test_") and file.endswith(".py"):
                        test_analysis["total_test_files"] += 1
                        
                        if "contract" in root:
                            test_analysis["contract_tests"] += 1
                        elif "unit" in root:
                            test_analysis["unit_tests"] += 1
                        elif "integration" in root:
                            test_analysis["integration_tests"] += 1
                        
                        # Extract test categories from filename
                        category = file.replace("test_", "").replace(".py", "")
                        test_analysis["test_categories"].append(category)
        
        self.analysis_results["test_coverage"] = test_analysis
        print(f"   ✅ Found {test_analysis['total_test_files']} test files")
    
    def analyze_performance_considerations(self):
        """Analyze performance-related implementations"""
        print("⚡ Analyzing performance considerations...")
        
        performance = {
            "async_operations": False,
            "database_indexing": False,
            "caching": False,
            "pagination": False,
            "connection_pooling": False,
            "background_tasks": False
        }
        
        # Check for performance patterns
        performance_patterns = {
            "async_operations": [r"async\s+def", r"await\s+", r"asyncio"],
            "database_indexing": [r"index", r"Index\(", r"db\.index"],
            "caching": [r"cache", r"redis", r"memcache"],
            "pagination": [r"limit", r"offset", r"page", r"pagina"],
            "connection_pooling": [r"pool", r"connection.*pool", r"asyncpg"],
            "background_tasks": [r"celery", r"background", r"task.*queue"]
        }
        
        # Search through implementation files
        for root, dirs, files in os.walk(self.project_root / "app"):
            if "__pycache__" in root:
                continue
                
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                file_path = Path(root) / file
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    for feature, patterns in performance_patterns.items():
                        if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                            performance[feature] = True
                            
                except Exception:
                    continue
        
        self.analysis_results["performance_considerations"] = performance
        
        implemented_optimizations = sum(performance.values())
        print(f"   ✅ Found {implemented_optimizations}/6 performance optimizations")
    
    def generate_recommendations(self):
        """Generate specific recommendations based on analysis"""
        print("📋 Generating recommendations...")
        
        recommendations = []
        
        # Security recommendations
        security = self.analysis_results["security_analysis"]
        if not security.get("rate_limiting", False):
            recommendations.append({
                "priority": "HIGH",
                "category": "Security",
                "title": "Implement Rate Limiting",
                "description": "Rate limiting not detected. Healthcare APIs should have robust rate limiting.",
                "action": "Add rate limiting middleware to prevent abuse and DoS attacks."
            })
        
        if not security.get("audit_logging", False):
            recommendations.append({
                "priority": "CRITICAL",
                "category": "HIPAA Compliance",
                "title": "Implement Comprehensive Audit Logging",
                "description": "HIPAA requires detailed audit logs for all PHI access.",
                "action": "Implement audit logging for all patient data operations."
            })
        
        # Healthcare compliance recommendations
        compliance = self.analysis_results["healthcare_compliance"]
        if not compliance.get("data_retention", False):
            recommendations.append({
                "priority": "HIGH",
                "category": "HIPAA Compliance",
                "title": "Implement Data Retention Policies",
                "description": "Healthcare data retention policies not clearly implemented.",
                "action": "Implement automated data retention and disposal policies."
            })
        
        # Performance recommendations
        performance = self.analysis_results["performance_considerations"]
        if not performance.get("caching", False):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Performance",
                "title": "Implement Caching Strategy",
                "description": "No caching mechanism detected for frequently accessed data.",
                "action": "Implement Redis caching for patient and visit data."
            })
        
        # Test coverage recommendations
        test_coverage = self.analysis_results["test_coverage"]
        if test_coverage["total_test_files"] < 10:
            recommendations.append({
                "priority": "HIGH",
                "category": "Quality Assurance",
                "title": "Increase Test Coverage", 
                "description": f"Only {test_coverage['total_test_files']} test files found. Healthcare applications need extensive testing.",
                "action": "Implement comprehensive unit, integration, and end-to-end tests."
            })
        
        # API endpoint recommendations
        endpoints = self.analysis_results["api_endpoints"]
        total_endpoints = sum(len(routes) for routes in endpoints.values())
        if total_endpoints == 0:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Implementation",
                "title": "Complete API Implementation",
                "description": "No API endpoints detected in analysis.",
                "action": "Complete implementation of all planned API endpoints."
            })
        
        self.analysis_results["recommendations"] = recommendations
        print(f"   ✅ Generated {len(recommendations)} recommendations")
    
    def identify_critical_findings(self):
        """Identify critical issues that need immediate attention"""
        print("🚨 Identifying critical findings...")
        
        critical_findings = []
        
        # Check for missing core files
        structure = self.analysis_results["architecture_analysis"]["structure"]
        core_files = ["app/main.py", "app/database.py", "requirements.txt"]
        
        for file_path in core_files:
            if not structure["key_components"][file_path]["exists"]:
                critical_findings.append({
                    "severity": "CRITICAL",
                    "category": "Infrastructure",
                    "issue": f"Missing core file: {file_path}",
                    "impact": "Application cannot function without this core component",
                    "action": "Implement missing core file immediately"
                })
        
        # Check security implementation
        security = self.analysis_results["security_analysis"]
        if not security.get("authentication", False):
            critical_findings.append({
                "severity": "CRITICAL",
                "category": "Security",
                "issue": "No authentication mechanism detected",
                "impact": "Unauthorized access to patient health information",
                "action": "Implement JWT-based authentication immediately"
            })
        
        # Check healthcare compliance
        compliance = self.analysis_results["healthcare_compliance"]
        if not compliance.get("phi_protection", False):
            critical_findings.append({
                "severity": "CRITICAL",
                "category": "HIPAA Compliance",
                "issue": "No PHI protection mechanisms detected",
                "impact": "HIPAA violation risk, potential legal consequences",
                "action": "Implement comprehensive PHI protection measures"
            })
        
        self.analysis_results["critical_findings"] = critical_findings
        print(f"   🚨 Found {len(critical_findings)} critical findings")
    
    def calculate_health_score(self):
        """Calculate overall system health score"""
        print("📊 Calculating health score...")
        
        # Base scoring
        total_possible = 100
        current_score = 0
        
        # Security score (30 points)
        security = self.analysis_results["security_analysis"]
        security_score = (sum(security.values()) / len(security)) * 30
        current_score += security_score
        
        # Compliance score (25 points)
        compliance = self.analysis_results["healthcare_compliance"]
        compliance_score = (sum(compliance.values()) / len(compliance)) * 25
        current_score += compliance_score
        
        # Performance score (20 points)
        performance = self.analysis_results["performance_considerations"]
        performance_score = (sum(performance.values()) / len(performance)) * 20
        current_score += performance_score
        
        # Test coverage score (15 points)
        test_coverage = self.analysis_results["test_coverage"]
        test_score = min(test_coverage["total_test_files"] / 10, 1.0) * 15
        current_score += test_score
        
        # Structure score (10 points)
        structure = self.analysis_results["architecture_analysis"]["structure"]
        key_files_present = sum(1 for comp in structure["key_components"].values() if comp["exists"])
        structure_score = (key_files_present / len(structure["key_components"])) * 10
        current_score += structure_score
        
        # Deduct for critical findings
        critical_count = len(self.analysis_results["critical_findings"])
        critical_deduction = min(critical_count * 15, 50)  # Max 50 point deduction
        current_score = max(0, current_score - critical_deduction)
        
        self.analysis_results["executive_summary"] = {
            "overall_health_score": round(current_score, 1),
            "security_score": round(security_score, 1),
            "compliance_score": round(compliance_score, 1),
            "performance_score": round(performance_score, 1),
            "test_score": round(test_score, 1),
            "structure_score": round(structure_score, 1),
            "critical_issues": critical_count,
            "total_recommendations": len(self.analysis_results["recommendations"])
        }
        
        print(f"   📊 Overall Health Score: {current_score:.1f}/100")
    
    def generate_comprehensive_report(self):
        """Generate the final comprehensive report"""
        print("\n🏁 Generating comprehensive analysis report...")
        
        # Run all analysis components
        self.analyze_project_structure()
        self.analyze_api_endpoints()
        self.analyze_database_models()
        self.analyze_security_implementation()
        self.analyze_healthcare_compliance()
        self.analyze_test_coverage()
        self.analyze_performance_considerations()
        self.generate_recommendations()
        self.identify_critical_findings()
        self.calculate_health_score()
        
        # Save detailed JSON report
        report_file = f"healthcare_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        # Generate executive summary
        self.print_executive_summary()
        
        return self.analysis_results
    
    def print_executive_summary(self):
        """Print formatted executive summary"""
        summary = self.analysis_results["executive_summary"]
        
        print("\n" + "="*80)
        print("PATIENT VISIT MANAGEMENT SYSTEM - HEALTHCARE API ANALYSIS REPORT")
        print("="*80)
        
        print(f"\n📊 EXECUTIVE SUMMARY")
        print(f"Analysis Date: {self.analysis_results['timestamp']}")
        print(f"Overall Health Score: {summary['overall_health_score']}/100")
        
        if summary['overall_health_score'] >= 80:
            status = "🟢 EXCELLENT"
        elif summary['overall_health_score'] >= 60:
            status = "🟡 GOOD"
        elif summary['overall_health_score'] >= 40:
            status = "🟠 NEEDS IMPROVEMENT"
        else:
            status = "🔴 CRITICAL"
        
        print(f"System Status: {status}")
        
        print(f"\n📈 SCORE BREAKDOWN")
        print(f"Security Score: {summary['security_score']}/30")
        print(f"HIPAA Compliance: {summary['compliance_score']}/25")
        print(f"Performance: {summary['performance_score']}/20") 
        print(f"Test Coverage: {summary['test_score']}/15")
        print(f"Architecture: {summary['structure_score']}/10")
        
        print(f"\n🚨 CRITICAL ISSUES")
        print(f"Critical Findings: {summary['critical_issues']}")
        if summary['critical_issues'] > 0:
            print("❌ IMMEDIATE ACTION REQUIRED")
        else:
            print("✅ No critical issues found")
        
        print(f"\n📋 RECOMMENDATIONS")
        print(f"Total Recommendations: {summary['total_recommendations']}")
        
        # Print top 3 critical findings
        critical_findings = self.analysis_results["critical_findings"][:3]
        if critical_findings:
            print(f"\n🚨 TOP CRITICAL ISSUES:")
            for i, finding in enumerate(critical_findings, 1):
                print(f"{i}. [{finding['severity']}] {finding['issue']}")
                print(f"   Impact: {finding['impact']}")
                print(f"   Action: {finding['action']}")
        
        # Print top 3 recommendations
        recommendations = self.analysis_results["recommendations"][:3]
        if recommendations:
            print(f"\n📋 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. [{rec['priority']}] {rec['title']}")
                print(f"   {rec['description']}")
        
        # API Endpoints Summary
        endpoints = self.analysis_results["api_endpoints"]
        total_endpoints = sum(len(routes) for routes in endpoints.values())
        print(f"\n🔗 API ENDPOINTS SUMMARY")
        print(f"Total Endpoints: {total_endpoints}")
        for category, routes in endpoints.items():
            if routes:
                print(f"   {category.title()}: {len(routes)} endpoints")
        
        # Database Models Summary
        models = self.analysis_results["database_design"]["models"]
        total_models = sum(len(info["classes"]) for info in models.values())
        print(f"\n🗄️  DATABASE MODELS SUMMARY")
        print(f"Total Models: {total_models}")
        for model_file, info in models.items():
            if info["classes"]:
                print(f"   {model_file}: {len(info['classes'])} models, {len(info['fields'])} fields")
        
        print(f"\n🧪 TESTING SUMMARY")
        test_coverage = self.analysis_results["test_coverage"]
        print(f"Test Files: {test_coverage['total_test_files']}")
        print(f"Contract Tests: {test_coverage['contract_tests']}")
        print(f"Unit Tests: {test_coverage['unit_tests']}")
        print(f"Integration Tests: {test_coverage['integration_tests']}")
        
        print("\n" + "="*80)
        print("RECOMMENDATIONS FOR PRODUCTION READINESS:")
        print("="*80)
        
        production_checklist = [
            ("🔒 Security", "Implement all authentication and authorization measures"),
            ("🏥 HIPAA Compliance", "Complete audit logging and PHI protection"),
            ("⚡ Performance", "Add caching and optimize database queries"),
            ("🧪 Testing", "Achieve 80%+ test coverage with end-to-end tests"),
            ("📚 Documentation", "Complete API documentation and deployment guides"),
            ("🚀 Deployment", "Setup production environment with monitoring"),
            ("🛡️  Monitoring", "Implement health checks and error tracking"),
            ("📊 Analytics", "Add performance monitoring and reporting")
        ]
        
        for category, action in production_checklist:
            print(f"{category}: {action}")
        
        print("\n" + "="*80)
        print("Analysis complete. Review detailed JSON report for full findings.")
        print("="*80 + "\n")

def main():
    """Main entry point for manual code analysis"""
    print("🏥 Starting Manual Healthcare API Analysis")
    print("="*60)
    
    analyzer = ManualCodeAnalyzer()
    
    try:
        report = analyzer.generate_comprehensive_report()
        
        # Exit with appropriate code
        health_score = report["executive_summary"]["overall_health_score"]
        critical_issues = len(report["critical_findings"])
        
        if critical_issues > 0:
            return 1  # Critical issues found
        elif health_score < 60:
            return 2  # Poor health score
        else:
            return 0  # All good
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)