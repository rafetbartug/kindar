def report_render_result(display, result, memory_before, memory_after):
    print("\n[RENDER]")
    print(f"Mode: {result['mode']}")
    print(f"File: {result['output_path']}")
    print(f"Size: {result['width']}x{result['height']}")

    if memory_before >= 0 and memory_after >= 0:
        delta = memory_after - memory_before
        print(f"RAM : {memory_before} -> {memory_after} kB ({delta:+} kB)")

    extra = result.get("extra", {})
    if "dpi" in extra:
        print(f"DPI : {extra['dpi']}")
    if "scale" in extra:
        print(f"Scale: {extra['scale']:.3f}")
    if "target_width" in extra and "target_height" in extra:
        print(f"Target: {extra['target_width']}x{extra['target_height']}")
    if "source_width" in extra and "source_height" in extra:
        print(f"Source: {extra['source_width']}x{extra['source_height']}")
    if "note" in extra:
        print(f"Note: {extra['note']}")
    if "cache_hit" in extra:
        print(f"Cache: {'yes' if extra['cache_hit'] else 'no'}")

    try:
        display.show_image(result["output_path"])
    except ValueError as e:
        print(f"Display failed: {e}")
    except Exception:
        print("Display failed: unexpected error.")
