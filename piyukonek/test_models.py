#!/usr/bin/env python3
"""
Test script to verify SQLAlchemy models can be imported without errors
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, Concern, SSC, Student
    print("✅ All models imported successfully!")
    print(f"✅ Concern model: {Concern}")
    print(f"✅ SSC model: {SSC}")
    print(f"✅ Student model: {Student}")
    
    # Test relationship access
    with app.app_context():
        print("\n✅ Testing relationships...")
        print(f"   Concern.resolver: {Concern.resolver}")
        print(f"   Concern.assigned_staff: {Concern.assigned_staff}")
        print(f"   Concern.processor: {Concern.processor}")
        print(f"   Concern.closer: {Concern.closer}")
        print("\n🎉 All relationships working correctly!")
        
except Exception as e:
    print(f"❌ Error importing models: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
