# test_imports.py
# Quick check that numpy, cv2, tensorflow, and fer import correctly.

def main():
    print("Testing imports...\n")

    try:
        import numpy as np
        print("numpy OK:", np.__version__)
    except Exception as e:
        print("numpy FAILED:", e)
        return

    try:
        import cv2
        print("cv2 OK")
        print("  module path:", getattr(cv2, "__file__", "unknown"))
        print("  has VideoCapture:", hasattr(cv2, "VideoCapture"))
        print("  has imshow:", hasattr(cv2, "imshow"))
        print("  has cvtColor:", hasattr(cv2, "cvtColor"))
        print("  has data:", hasattr(cv2, "data"))
    except Exception as e:
        print("cv2 FAILED:", e)
        return

    try:
        import tensorflow as tf
        print("tensorflow OK:", tf.__version__)
    except Exception as e:
        print("tensorflow FAILED:", e)
        return

    try:
        from fer import FER
        detector = FER(mtcnn=False)
        print("fer OK: detector created successfully")
    except Exception as e:
        print("fer FAILED:", e)
        return

    print("\nAll imports worked.")

if __name__ == "__main__":
    main()
