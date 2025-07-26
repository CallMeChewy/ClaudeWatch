# File: UserConditionDetector.py
# Path: /home/herb/Desktop/AndyLibrary/UserConditionDetector.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 10:18AM

"""
User Condition Detector
Detects user's network/hardware conditions and provides tailored recommendations
"""

import time
import requests
import psutil
import platform
import sqlite3
import tempfile
import os
from pathlib import Path
from datetime import datetime

class UserConditionDetector:
    """Detect user conditions and provide performance predictions"""
    
    def __init__(self):
        self.conditions = {}
        self.recommendations = []
        
    def detect_network_speed(self, test_duration=3):
        """Detect user's actual network speed"""
        print("🌐 Testing your network speed...")
        
        # Use a small test download to measure speed
        test_urls = [
            "https://httpbin.org/bytes/1048576",  # 1MB test file
            "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
        ]
        
        speeds = []
        for url in test_urls:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10, stream=True)
                
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    downloaded += len(chunk)
                    if time.time() - start_time > test_duration:
                        break
                
                elapsed = time.time() - start_time
                if elapsed > 0 and downloaded > 0:
                    speed_mbps = (downloaded * 8) / (elapsed * 1000000)  # Convert to Mbps
                    speeds.append(speed_mbps)
                    print(f"   📡 Test {len(speeds)}: {speed_mbps:.1f} Mbps")
                
            except Exception as e:
                print(f"   ⚠️ Network test failed: {e}")
                continue
        
        if speeds:
            avg_speed = sum(speeds) / len(speeds)
            self.conditions['network_mbps'] = avg_speed
            print(f"   ✅ Average speed: {avg_speed:.1f} Mbps")
            return avg_speed
        else:
            print("   ❌ Could not determine network speed")
            self.conditions['network_mbps'] = 5.0  # Conservative estimate
            return 5.0
    
    def detect_hardware_specs(self):
        """Detect user's hardware specifications"""
        print("💻 Analyzing your hardware...")
        
        # CPU Information
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory Information
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        memory_available_gb = memory.available / (1024**3)
        
        # Disk Information
        disk = psutil.disk_usage('/')
        disk_free_gb = disk.free / (1024**3)
        
        # System Information
        system_info = {
            'platform': platform.system(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
        
        self.conditions.update({
            'cpu_cores': cpu_count,
            'cpu_freq_mhz': cpu_freq.current if cpu_freq else 2000,
            'cpu_usage': cpu_percent,
            'memory_gb': memory_gb,
            'memory_available_gb': memory_available_gb,
            'disk_free_gb': disk_free_gb,
            'platform': system_info['platform']
        })
        
        print(f"   🔧 CPU: {cpu_count} cores @ {cpu_freq.current if cpu_freq else 'Unknown'} MHz")
        print(f"   🧠 RAM: {memory_gb:.1f} GB total, {memory_available_gb:.1f} GB available")
        print(f"   💾 Disk: {disk_free_gb:.1f} GB free")
        print(f"   📱 Platform: {system_info['platform']}")
        
        return self.conditions
    
    def classify_user_type(self):
        """Classify user based on detected conditions"""
        network_speed = self.conditions.get('network_mbps', 5)
        memory_gb = self.conditions.get('memory_gb', 4)
        cpu_cores = self.conditions.get('cpu_cores', 2)
        
        # Network classification
        if network_speed >= 20:
            network_class = "fast"
        elif network_speed >= 10:
            network_class = "medium"
        elif network_speed >= 5:
            network_class = "slow"
        else:
            network_class = "very_slow"
        
        # Hardware classification
        if memory_gb >= 8 and cpu_cores >= 4:
            hardware_class = "modern"
        elif memory_gb >= 4 and cpu_cores >= 2:
            hardware_class = "budget"
        else:
            hardware_class = "limited"
        
        self.conditions['network_class'] = network_class
        self.conditions['hardware_class'] = hardware_class
        
        return network_class, hardware_class
    
    def predict_performance(self, database_size_mb=10.3):
        """Predict performance for user's specific conditions"""
        print("🔮 Predicting performance for your setup...")
        
        network_speed = self.conditions.get('network_mbps', 5)
        network_class = self.conditions.get('network_class', 'slow')
        hardware_class = self.conditions.get('hardware_class', 'budget')
        
        # Calculate download time
        download_speed_mbps = network_speed * 0.8  # 80% efficiency
        download_time_seconds = (database_size_mb * 8) / download_speed_mbps if download_speed_mbps > 0 else 60
        
        # Processing time based on hardware
        processing_times = {
            'modern': 0.002,
            'budget': 0.005,
            'limited': 0.010
        }
        processing_time = processing_times.get(hardware_class, 0.005)
        
        total_time = download_time_seconds + processing_time
        
        # Memory usage prediction
        memory_usage_mb = database_size_mb * 0.15  # ~15% of database size in memory
        
        self.conditions.update({
            'predicted_download_time': download_time_seconds,
            'predicted_processing_time': processing_time,
            'predicted_total_time': total_time,
            'predicted_memory_usage_mb': memory_usage_mb
        })
        
        print(f"   📥 Download: {download_time_seconds:.1f}s")
        print(f"   🔄 Processing: {processing_time:.3f}s")
        print(f"   ⏱️ Total wait: {total_time:.1f}s")
        print(f"   🧠 Memory: {memory_usage_mb:.1f}MB")
        
        return {
            'download_time': download_time_seconds,
            'processing_time': processing_time,
            'total_time': total_time,
            'memory_usage': memory_usage_mb
        }
    
    def generate_recommendations(self):
        """Generate specific recommendations based on user conditions"""
        total_time = self.conditions.get('predicted_total_time', 30)
        network_class = self.conditions.get('network_class', 'slow')
        hardware_class = self.conditions.get('hardware_class', 'budget')
        memory_available = self.conditions.get('memory_available_gb', 2)
        
        self.recommendations = []
        
        # Time-based recommendations
        if total_time > 30:
            self.recommendations.append({
                'type': 'warning',
                'title': 'Slow Connection Detected',
                'message': f'Download will take ~{total_time:.0f}s. Consider using WiFi if on mobile data.',
                'action': 'Consider background download or progressive loading'
            })
        elif total_time > 15:
            self.recommendations.append({
                'type': 'caution',
                'title': 'Moderate Wait Time',
                'message': f'Download will take ~{total_time:.0f}s. Please be patient.',
                'action': 'Show progress indicator during download'
            })
        else:
            self.recommendations.append({
                'type': 'success',
                'title': 'Fast Connection',
                'message': f'Download will complete quickly (~{total_time:.0f}s).',
                'action': 'Standard download recommended'
            })
        
        # Network-specific recommendations
        if network_class == 'very_slow':
            self.recommendations.append({
                'type': 'error',
                'title': 'Very Slow Network',
                'message': 'Consider using a faster connection or download during off-peak hours.',
                'action': 'Offer lite version or cached mode'
            })
        elif network_class == 'slow':
            self.recommendations.append({
                'type': 'warning',
                'title': 'Limited Bandwidth',
                'message': 'Close other applications using internet to speed up download.',
                'action': 'Suggest optimal download timing'
            })
        
        # Hardware-specific recommendations
        if hardware_class == 'limited':
            self.recommendations.append({
                'type': 'caution',
                'title': 'Limited Hardware',
                'message': 'Close other applications to improve performance.',
                'action': 'Use conservative memory settings'
            })
        
        # Memory-specific recommendations
        if memory_available < 1:
            self.recommendations.append({
                'type': 'warning',
                'title': 'Low Memory',
                'message': f'Only {memory_available:.1f}GB RAM available. Close other applications.',
                'action': 'Use disk-based caching instead of memory'
            })
        
        return self.recommendations
    
    def display_user_report(self):
        """Display complete user condition report with recommendations"""
        print("\\n📊 YOUR SYSTEM PERFORMANCE REPORT")
        print("=" * 60)
        
        # System Summary
        print("🖥️ SYSTEM SUMMARY:")
        print(f"   Network: {self.conditions['network_mbps']:.1f} Mbps ({self.conditions['network_class']})")
        print(f"   Hardware: {self.conditions['hardware_class']} ({self.conditions['cpu_cores']} cores, {self.conditions['memory_gb']:.1f}GB RAM)")
        print(f"   Platform: {self.conditions['platform']}")
        
        # Performance Prediction
        print(f"\\n⏱️ PREDICTED PERFORMANCE:")
        print(f"   Download time: {self.conditions['predicted_download_time']:.1f}s")
        print(f"   Processing time: {self.conditions['predicted_processing_time']:.3f}s")
        print(f"   Total wait time: {self.conditions['predicted_total_time']:.1f}s")
        print(f"   Memory usage: {self.conditions['predicted_memory_usage_mb']:.1f}MB")
        
        # Recommendations
        print(f"\\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(self.recommendations, 1):
            icon = {'success': '✅', 'caution': '⚠️', 'warning': '🚨', 'error': '❌'}.get(rec['type'], 'ℹ️')
            print(f"   {icon} {rec['title']}")
            print(f"      {rec['message']}")
            print(f"      Action: {rec['action']}")
            if i < len(self.recommendations):
                print()
        
        # User Options
        print(f"\\n🎯 RECOMMENDED OPTIONS:")
        total_time = self.conditions['predicted_total_time']
        
        if total_time <= 10:
            print("   🚀 FULL DOWNLOAD - Your connection is fast enough for the best experience")
            print("      • Download full 10MB database")
            print("      • Enable Python caching for blazing speed")
            print("      • Expected wait: Good user experience")
        elif total_time <= 30:
            print("   ⚡ STANDARD DOWNLOAD - Moderate wait time")
            print("      • Download full database with progress indicator")
            print("      • Show estimated time remaining")
            print("      • Enable background processing")
        else:
            print("   🔄 PROGRESSIVE LOADING - Optimize for slow connections")
            print("      • Download essential data first (categories, recent books)")
            print("      • Load additional content in background")
            print("      • Offer lite mode with reduced features")
            print("      • Consider download scheduling for off-peak hours")
        
        return self.recommendations
    
    def get_optimal_strategy(self):
        """Get optimal caching strategy for user's conditions"""
        memory_available = self.conditions.get('memory_available_gb', 2)
        hardware_class = self.conditions.get('hardware_class', 'budget')
        total_time = self.conditions.get('predicted_total_time', 30)
        
        if memory_available >= 1 and hardware_class in ['modern', 'budget']:
            strategy = "python_cache"
            reason = "Fast Python dict caching - optimal for your hardware"
        elif memory_available >= 0.5:
            strategy = "memory_db"
            reason = "In-memory SQLite database - good balance"
        else:
            strategy = "disk_optimized"
            reason = "Optimized disk access - conserves memory"
        
        return {
            'strategy': strategy,
            'reason': reason,
            'estimated_performance': '0.0001s queries' if strategy == 'python_cache' else '0.001s queries'
        }

def run_user_assessment():
    """Run complete user condition assessment"""
    print("🔍 ANALYZING YOUR SYSTEM FOR OPTIMAL PERFORMANCE")
    print("=" * 70)
    
    detector = UserConditionDetector()
    
    # Run all detections
    detector.detect_network_speed(test_duration=2)
    detector.detect_hardware_specs()
    detector.classify_user_type()
    detector.predict_performance()
    detector.generate_recommendations()
    
    # Display comprehensive report
    detector.display_user_report()
    
    # Get optimal strategy
    strategy = detector.get_optimal_strategy()
    print(f"\\n🎯 OPTIMAL STRATEGY FOR YOU:")
    print(f"   Strategy: {strategy['strategy']}")
    print(f"   Reason: {strategy['reason']}")
    print(f"   Performance: {strategy['estimated_performance']}")
    
    return detector

if __name__ == "__main__":
    assessment = run_user_assessment()