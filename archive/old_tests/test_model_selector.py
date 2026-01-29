"""
Test script for model selector functionality
"""
from config import Config


def test_model_config():
    """Test that the model configuration is properly set up"""
    print("Testing Model Configuration...")
    print("-" * 80)
    
    # Test 1: Check AVAILABLE_MODELS exists
    assert hasattr(Config, 'AVAILABLE_MODELS'), "Config.AVAILABLE_MODELS not found"
    print("✅ AVAILABLE_MODELS exists")
    
    # Test 2: Check it has 3 models
    assert len(Config.AVAILABLE_MODELS) == 3, f"Expected 3 models, got {len(Config.AVAILABLE_MODELS)}"
    print(f"✅ Found {len(Config.AVAILABLE_MODELS)} models")
    
    # Test 3: Check model names
    expected_models = {
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite", 
        "gemini-3-flash"
    }
    actual_models = {info["name"] for info in Config.AVAILABLE_MODELS.values()}
    assert actual_models == expected_models, f"Model names don't match. Expected {expected_models}, got {actual_models}"
    print("✅ All model names are correct")
    
    # Test 4: Check default model
    assert Config.DEFAULT_MODEL in actual_models, f"DEFAULT_MODEL '{Config.DEFAULT_MODEL}' not in available models"
    print(f"✅ DEFAULT_MODEL is '{Config.DEFAULT_MODEL}'")
    
    # Test 5: Display all models
    print("\n" + "=" * 80)
    print("AVAILABLE MODELS:")
    print("=" * 80)
    for key, info in Config.AVAILABLE_MODELS.items():
        print(f"  [{key}] {info['name']}")
        print(f"      {info['description']}")
        print(f"      Rate limits: {info['rpm']} RPM / {info['rpd']} RPD\n")
    
    print("=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)


if __name__ == "__main__":
    test_model_config()
