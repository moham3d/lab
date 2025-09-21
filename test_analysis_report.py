#!/usr/bin/env python3
"""
Comprehensive Test and Analysis Tool for Patient Visit Management System
Healthcare API Testing and Report Generation
"""

import asyncio
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import os

# Test Analysis Classes
class TestResult:
    def __init__(self, name: str, status: str, details: str = "", execution_time: float = 0.0):
        self.name = name
        self.status = status  # PASS, FAIL, SKIP, ERROR
        self.details = details
        self.execution_time = execution_time
        self.timestamp = datetime.now()

class SecurityFinding:
    def __init__(self, severity: str, title: str, description: str, file_path: str = "", recommendation: str = ""):
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW
        self.title = title
        self.description = description
        self.file_path = file_path
        self.recommendation = recommendation

class PerformanceMetric:
    def __init__(self, name: str, value: float, unit: str, benchmark: float = None):
        self.name = name
        self.value = value
        self.unit = unit
        self.benchmark = benchmark
        self.is_within_benchmark = benchmark is None or value <= benchmark

class ComprehensiveAnalyzer:
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.security_findings: List[SecurityFinding] = []
        self.performance_metrics: List[PerformanceMetric] = []
        self.code_analysis: Dict[str, Any] = {}
        self.start_time = datetime.now()
        
        # Setup environment
        os.environ['ENVIRONMENT'] = 'test'
        
        # Change to test env
        if Path('.env.test').exists():
            os.environ['ENV_FILE'] = '.env.test'

    def log(self, message: str, level: str = "INFO"):
        """Log analysis progress"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def run_command(self, command: str, cwd: str = None) -> tuple:
        """Execute a command and return output, error, and return code"""
        try:
            result = subprocess.run(
                command.split(),
                cwd=cwd or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", 1
        except Exception as e:
            return "", str(e), 1

    def analyze_code_structure(self):
        """Analyze the codebase structure and architecture"""
        self.log("Starting code structure analysis")
        
        analysis = {
            "total_files": 0,
            "python_files": 0,
            "test_files": 0,
            "api_endpoints": 0,
            "models": 0,
            "services": 0,
            "schemas": 0,
            "directories": []
        }
        
        try:
            # Count files and structure
            for root, dirs, files in os.walk("app"):
                if "__pycache__" in root:
                    continue
                    
                analysis["directories"].append(root)
                
                for file in files:
                    if file.endswith('.py'):
                        analysis["python_files"] += 1
                        analysis["total_files"] += 1
                        
                        if "test" in file:
                            analysis["test_files"] += 1
                        elif "endpoints" in root:
                            analysis["api_endpoints"] += 1
                        elif "models" in root:
                            analysis["models"] += 1
                        elif "services" in root:
                            analysis["services"] += 1
                        elif "schemas" in root:
                            analysis["schemas"] += 1
            
            self.code_analysis["structure"] = analysis
            self.log(f"Code analysis complete: {analysis['python_files']} Python files analyzed")
            
        except Exception as e:
            self.log(f"Code structure analysis failed: {e}", "ERROR")
            self.test_results.append(TestResult(
                "Code Structure Analysis", 
                "ERROR", 
                f"Failed to analyze code structure: {e}"
            ))

    def check_dependencies_and_setup(self):
        """Check if all dependencies are installed and environment is set up"""
        self.log("Checking dependencies and environment setup")
        
        try:
            # Check Python environment
            stdout, stderr, code = self.run_command("python --version")
            if code == 0:
                self.test_results.append(TestResult(
                    "Python Environment", 
                    "PASS", 
                    f"Python version: {stdout.strip()}"
                ))
            else:
                self.test_results.append(TestResult(
                    "Python Environment", 
                    "FAIL", 
                    f"Python check failed: {stderr}"
                ))
            
            # Check key dependencies
            key_dependencies = [
                "fastapi", "sqlalchemy", "asyncpg", "aiosqlite", 
                "pydantic", "pytest", "httpx"
            ]
            
            for dep in key_dependencies:
                try:
                    __import__(dep.replace("-", "_"))
                    self.test_results.append(TestResult(
                        f"Dependency: {dep}", 
                        "PASS", 
                        f"{dep} is available"
                    ))
                except ImportError:
                    self.test_results.append(TestResult(
                        f"Dependency: {dep}", 
                        "FAIL", 
                        f"{dep} is not installed"
                    ))
            
        except Exception as e:
            self.log(f"Dependency check failed: {e}", "ERROR")
            self.test_results.append(TestResult(
                "Dependency Check", 
                "ERROR", 
                f"Failed to check dependencies: {e}"
            ))

    def run_static_analysis(self):
        """Run static code analysis tools"""
        self.log("Running static code analysis")
        
        # Check for common security issues
        self.check_security_patterns()
        
        # Run flake8 for code quality
        try:
            stdout, stderr, code = self.run_command("python -m flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics")
            if code == 0:
                self.test_results.append(TestResult(
                    "Static Analysis (Flake8)", 
                    "PASS", 
                    "No critical issues found"
                ))
            else:
                self.test_results.append(TestResult(
                    "Static Analysis (Flake8)", 
                    "FAIL", 
                    f"Issues found:\n{stdout}\n{stderr}"
                ))
        except Exception as e:
            self.test_results.append(TestResult(
                "Static Analysis (Flake8)", 
                "ERROR", 
                f"Failed to run flake8: {e}"
            ))

    def check_security_patterns(self):
        """Check for common security patterns and vulnerabilities"""
        self.log("Checking security patterns")
        
        security_patterns = [
            ("hardcoded_secrets", r"password.*=.*['\"][^'\"]+['\"]", "HIGH"),
            ("sql_injection", r"execute\(.*\+.*\)", "CRITICAL"),
            ("debug_mode", r"debug.*=.*True", "MEDIUM"),
            ("no_csrf_protection", r"@app\.route.*methods.*POST", "MEDIUM"),
        ]
        
        try:
            for root, dirs, files in os.walk("app"):
                if "__pycache__" in root:
                    continue
                    
                for file in files:
                    if not file.endswith('.py'):
                        continue
                        
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Check for hardcoded secrets (basic)
                        if "password" in content.lower() and ("=" in content and ("\"" in content or "'" in content)):
                            # This is a very basic check
                            if not any(safe in content.lower() for safe in ["getenv", "environ", "settings", "config"]):
                                self.security_findings.append(SecurityFinding(
                                    "MEDIUM",
                                    "Potential Hardcoded Password",
                                    f"File {file_path} may contain hardcoded credentials",
                                    file_path,
                                    "Use environment variables or secure configuration"
                                ))
                        
                        # Check for debug mode
                        if "debug=True" in content or "DEBUG = True" in content:
                            self.security_findings.append(SecurityFinding(
                                "MEDIUM",
                                "Debug Mode Enabled",
                                f"Debug mode found in {file_path}",
                                file_path,
                                "Disable debug mode in production"
                            ))
                            
                    except Exception as e:
                        continue
                        
        except Exception as e:
            self.log(f"Security pattern check failed: {e}", "ERROR")

    def test_api_imports(self):
        """Test if all API modules can be imported"""
        self.log("Testing API module imports")
        
        api_modules = [
            "app.main",
            "app.core.config",
            "app.database",
            "app.api.v1.api",
            "app.models.user",
            "app.models.patient",
            "app.services.auth_service",
        ]
        
        for module in api_modules:
            try:
                __import__(module)
                self.test_results.append(TestResult(
                    f"Import: {module}", 
                    "PASS", 
                    f"Successfully imported {module}"
                ))
            except ImportError as e:
                self.test_results.append(TestResult(
                    f"Import: {module}", 
                    "FAIL", 
                    f"Failed to import {module}: {e}"
                ))
            except Exception as e:
                self.test_results.append(TestResult(
                    f"Import: {module}", 
                    "ERROR", 
                    f"Error importing {module}: {e}"
                ))

    def analyze_database_models(self):
        """Analyze database models and relationships"""
        self.log("Analyzing database models")
        
        try:
            models_dir = Path("app/models")
            if not models_dir.exists():
                self.test_results.append(TestResult(
                    "Database Models", 
                    "FAIL", 
                    "Models directory not found"
                ))
                return
            
            model_files = list(models_dir.glob("*.py"))
            model_count = len([f for f in model_files if f.name != "__init__.py"])
            
            self.test_results.append(TestResult(
                "Database Models Count", 
                "PASS", 
                f"Found {model_count} model files"
            ))
            
            # Check for key models
            key_models = ["user.py", "patient.py", "visit.py", "assessment.py", "document.py"]
            for model in key_models:
                model_path = models_dir / model
                if model_path.exists():
                    self.test_results.append(TestResult(
                        f"Model: {model}", 
                        "PASS", 
                        f"{model} exists"
                    ))
                else:
                    self.test_results.append(TestResult(
                        f"Model: {model}", 
                        "FAIL", 
                        f"{model} not found"
                    ))
                    
        except Exception as e:
            self.test_results.append(TestResult(
                "Database Models Analysis", 
                "ERROR", 
                f"Failed to analyze models: {e}"
            ))

    def test_configuration_loading(self):
        """Test configuration loading with different environments"""
        self.log("Testing configuration loading")
        
        try:
            # Test with test environment
            os.environ['ENV_FILE'] = '.env.test'
            
            # Try importing settings
            from app.core.config import settings
            
            self.test_results.append(TestResult(
                "Configuration Loading", 
                "PASS", 
                f"Successfully loaded settings: {settings.PROJECT_NAME}"
            ))
            
            # Check critical configuration values
            critical_configs = {
                "SECRET_KEY": settings.SECRET_KEY,
                "DATABASE_URL": settings.DATABASE_URL,
                "API_V1_STR": settings.API_V1_STR,
            }
            
            for config_name, config_value in critical_configs.items():
                if config_value:
                    self.test_results.append(TestResult(
                        f"Config: {config_name}", 
                        "PASS", 
                        f"{config_name} is configured"
                    ))
                else:
                    self.test_results.append(TestResult(
                        f"Config: {config_name}", 
                        "FAIL", 
                        f"{config_name} is not set"
                    ))
                    
        except Exception as e:
            self.test_results.append(TestResult(
                "Configuration Loading", 
                "ERROR", 
                f"Failed to load configuration: {e}"
            ))

    def test_database_connection(self):
        """Test database connectivity (if available)"""
        self.log("Testing database connectivity")
        
        try:
            # For testing, we'll use SQLite
            import aiosqlite
            import asyncio
            
            async def test_db():
                try:
                    async with aiosqlite.connect("test.db") as db:
                        await db.execute("SELECT 1")
                        return True
                except Exception as e:
                    return False, str(e)
            
            result = asyncio.run(test_db())
            if result is True:
                self.test_results.append(TestResult(
                    "Database Connection", 
                    "PASS", 
                    "Successfully connected to test database"
                ))
            else:
                self.test_results.append(TestResult(
                    "Database Connection", 
                    "FAIL", 
                    f"Database connection failed: {result[1] if isinstance(result, tuple) else 'Unknown error'}"
                ))
                
        except Exception as e:
            self.test_results.append(TestResult(
                "Database Connection", 
                "ERROR", 
                f"Failed to test database connection: {e}"
            ))

    def check_file_structure_compliance(self):
        """Check if file structure follows healthcare application standards"""
        self.log("Checking file structure compliance")
        
        required_structure = {
            "app/": "Main application directory",
            "app/api/": "API endpoints",
            "app/core/": "Core functionality",
            "app/models/": "Database models",
            "app/schemas/": "Pydantic schemas",
            "app/services/": "Business logic services",
            "app/tests/": "Test suite",
            "app/utils/": "Utility functions",
            "alembic/": "Database migrations",
            "requirements.txt": "Python dependencies",
            "docker-compose.yml": "Container orchestration",
            ".env.example": "Environment template"
        }
        
        for path, description in required_structure.items():
            full_path = Path(path)
            if full_path.exists():
                self.test_results.append(TestResult(
                    f"Structure: {path}", 
                    "PASS", 
                    f"{description} - Present"
                ))
            else:
                self.test_results.append(TestResult(
                    f"Structure: {path}", 
                    "FAIL", 
                    f"{description} - Missing"
                ))

    def generate_comprehensive_report(self):
        """Generate the final comprehensive report"""
        self.log("Generating comprehensive analysis report")
        
        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t.status == "PASS"])
        failed_tests = len([t for t in self.test_results if t.status == "FAIL"])
        error_tests = len([t for t in self.test_results if t.status == "ERROR"])
        
        # Categorize security findings
        critical_security = len([f for f in self.security_findings if f.severity == "CRITICAL"])
        high_security = len([f for f in self.security_findings if f.severity == "HIGH"])
        medium_security = len([f for f in self.security_findings if f.severity == "MEDIUM"])
        low_security = len([f for f in self.security_findings if f.severity == "LOW"])
        
        execution_time = (datetime.now() - self.start_time).total_seconds()
        
        # Generate report
        report = {
            "executive_summary": {
                "analysis_date": self.start_time.isoformat(),
                "execution_time_seconds": execution_time,
                "total_tests_run": total_tests,
                "tests_passed": passed_tests,
                "tests_failed": failed_tests,
                "tests_with_errors": error_tests,
                "pass_rate_percent": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "security_findings": {
                    "critical": critical_security,
                    "high": high_security,
                    "medium": medium_security,
                    "low": low_security,
                    "total": len(self.security_findings)
                },
                "overall_health_score": self.calculate_health_score()
            },
            "technical_analysis": {
                "code_structure": self.code_analysis,
                "dependency_status": "See detailed test results",
                "configuration_status": "See detailed test results"
            },
            "test_results": [
                {
                    "name": test.name,
                    "status": test.status,
                    "details": test.details,
                    "execution_time": test.execution_time,
                    "timestamp": test.timestamp.isoformat()
                } for test in self.test_results
            ],
            "security_findings": [
                {
                    "severity": finding.severity,
                    "title": finding.title,
                    "description": finding.description,
                    "file_path": finding.file_path,
                    "recommendation": finding.recommendation
                } for finding in self.security_findings
            ],
            "performance_metrics": [
                {
                    "name": metric.name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "benchmark": metric.benchmark,
                    "within_benchmark": metric.is_within_benchmark
                } for metric in self.performance_metrics
            ],
            "recommendations": self.generate_recommendations()
        }
        
        # Save report to file
        report_file = f"comprehensive_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Comprehensive report saved to {report_file}")
        
        # Print summary to console
        self.print_summary_report(report)
        
        return report

    def calculate_health_score(self) -> float:
        """Calculate overall system health score (0-100)"""
        if not self.test_results:
            return 0.0
        
        # Base score from test results
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t.status == "PASS"])
        base_score = (passed_tests / total_tests) * 100
        
        # Deduct points for security findings
        security_deductions = 0
        for finding in self.security_findings:
            if finding.severity == "CRITICAL":
                security_deductions += 20
            elif finding.severity == "HIGH":
                security_deductions += 10
            elif finding.severity == "MEDIUM":
                security_deductions += 5
            elif finding.severity == "LOW":
                security_deductions += 1
        
        final_score = max(0, base_score - security_deductions)
        return min(100, final_score)

    def generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        # Test failure recommendations
        failed_tests = [t for t in self.test_results if t.status in ["FAIL", "ERROR"]]
        if failed_tests:
            recommendations.append({
                "priority": "HIGH",
                "category": "Testing",
                "title": "Fix Failed Tests",
                "description": f"{len(failed_tests)} tests are failing. Address these before production deployment.",
                "action": "Review and fix failing tests to ensure system reliability."
            })
        
        # Security recommendations
        critical_security = [f for f in self.security_findings if f.severity == "CRITICAL"]
        if critical_security:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Security",
                "title": "Critical Security Issues",
                "description": f"{len(critical_security)} critical security issues found.",
                "action": "Address all critical security vulnerabilities immediately."
            })
        
        # Code structure recommendations
        if "structure" in self.code_analysis:
            structure = self.code_analysis["structure"]
            if structure.get("test_files", 0) < structure.get("python_files", 0) * 0.3:
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": "Testing",
                    "title": "Insufficient Test Coverage",
                    "description": "Test coverage appears low based on file count analysis.",
                    "action": "Increase test coverage to at least 80% for production readiness."
                })
        
        # Default recommendations for healthcare applications
        recommendations.extend([
            {
                "priority": "HIGH",
                "category": "HIPAA Compliance",
                "title": "HIPAA Audit Trail",
                "description": "Ensure all patient data access is logged for HIPAA compliance.",
                "action": "Implement comprehensive audit logging for all patient data operations."
            },
            {
                "priority": "HIGH",
                "category": "Security",
                "title": "Data Encryption",
                "description": "Verify all patient health information (PHI) is encrypted at rest and in transit.",
                "action": "Implement AES-256 encryption for sensitive data storage."
            },
            {
                "priority": "MEDIUM",
                "category": "Performance",
                "title": "Response Time Optimization",
                "description": "Healthcare applications should maintain <500ms response times.",
                "action": "Conduct performance testing and optimize slow endpoints."
            }
        ])
        
        return recommendations

    def print_summary_report(self, report: Dict):
        """Print a formatted summary report to console"""
        print("\n" + "="*80)
        print("PATIENT VISIT MANAGEMENT SYSTEM - COMPREHENSIVE ANALYSIS REPORT")
        print("="*80)
        
        summary = report["executive_summary"]
        print(f"\n📊 EXECUTIVE SUMMARY")
        print(f"Analysis Date: {summary['analysis_date']}")
        print(f"Execution Time: {summary['execution_time_seconds']:.2f} seconds")
        print(f"Overall Health Score: {summary['overall_health_score']:.1f}/100")
        
        print(f"\n🧪 TEST RESULTS")
        print(f"Total Tests: {summary['total_tests_run']}")
        print(f"Passed: {summary['tests_passed']} ({summary['pass_rate_percent']:.1f}%)")
        print(f"Failed: {summary['tests_failed']}")
        print(f"Errors: {summary['tests_with_errors']}")
        
        security = summary['security_findings']
        print(f"\n🔒 SECURITY ANALYSIS")
        print(f"Critical Issues: {security['critical']}")
        print(f"High Issues: {security['high']}")
        print(f"Medium Issues: {security['medium']}")
        print(f"Low Issues: {security['low']}")
        print(f"Total Security Findings: {security['total']}")
        
        print(f"\n📋 TOP RECOMMENDATIONS")
        for i, rec in enumerate(report["recommendations"][:5], 1):
            print(f"{i}. [{rec['priority']}] {rec['title']}")
            print(f"   {rec['description']}")
        
        # Print detailed test results
        print(f"\n📝 DETAILED TEST RESULTS")
        print("-" * 80)
        
        for test in report["test_results"]:
            status_symbol = {
                "PASS": "✅",
                "FAIL": "❌", 
                "ERROR": "⚠️",
                "SKIP": "⏭️"
            }.get(test["status"], "❓")
            
            print(f"{status_symbol} {test['name']}: {test['status']}")
            if test["details"] and test["status"] != "PASS":
                # Truncate long details
                details = test["details"][:200] + "..." if len(test["details"]) > 200 else test["details"]
                print(f"   Details: {details}")
        
        print("\n" + "="*80)
        print("Analysis complete. See full JSON report for detailed findings.")
        print("="*80 + "\n")

    async def run_comprehensive_analysis(self):
        """Run the complete analysis suite"""
        self.log("Starting comprehensive analysis of Patient Visit Management System")
        
        # Phase 1: Environment and Setup
        self.log("Phase 1: Environment and Setup Analysis")
        self.check_dependencies_and_setup()
        self.test_configuration_loading()
        self.check_file_structure_compliance()
        
        # Phase 2: Code Analysis
        self.log("Phase 2: Code Structure and Quality Analysis")
        self.analyze_code_structure()
        self.test_api_imports()
        self.analyze_database_models()
        
        # Phase 3: Security Analysis
        self.log("Phase 3: Security and Compliance Analysis")
        self.run_static_analysis()
        
        # Phase 4: Infrastructure Testing
        self.log("Phase 4: Infrastructure and Database Testing")
        self.test_database_connection()
        
        # Phase 5: Generate Report
        self.log("Phase 5: Report Generation")
        report = self.generate_comprehensive_report()
        
        return report

def main():
    """Main entry point for comprehensive analysis"""
    analyzer = ComprehensiveAnalyzer()
    
    try:
        # Run the analysis
        report = asyncio.run(analyzer.run_comprehensive_analysis())
        
        # Exit with appropriate code based on results
        if report["executive_summary"]["overall_health_score"] < 50:
            sys.exit(1)  # Major issues found
        elif report["executive_summary"]["tests_failed"] > 0:
            sys.exit(2)  # Some tests failed
        else:
            sys.exit(0)  # All good
            
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Analysis failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()