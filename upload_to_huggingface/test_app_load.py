try:
    print("Importing app...")
    import app
    print("Import success!")
except Exception as e:
    print(f"Import failed: {e}")
except SystemExit as se:
    print(f"SystemExit: {se}")
