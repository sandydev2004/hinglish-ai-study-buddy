"""
generate_test_samples.py
------------------------
Helper script to automatically generate 3 test PDFs for testing Week 1 features:
1. short_notes.pdf      -> A valid digital PDF with typed Operating Systems notes.
2. empty.pdf            -> An empty 0-byte file to test empty document error handling.
3. scanned_dummy.pdf    -> A PDF with a drawing/canvas but NO text (simulates scanned/image PDF).

Run this script once inside your virtual environment:
    python generate_test_samples.py
"""

import os
import fitz  # PyMuPDF


def create_samples():
    output_dir = os.path.join(os.path.dirname(__file__), "test_samples")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Creating test files in: {output_dir}\n")

    # -------------------------------------------------------------
    # 1. Valid Typed Notes PDF (Operating Systems - Deadlock Notes)
    # -------------------------------------------------------------
    doc1 = fitz.open()
    page1 = doc1.new_page(width=595, height=842)  # A4 size

    sample_content = (
        "Operating Systems: Unit 3 - Deadlocks and Process Synchronization\n\n"
        "1. What is a Deadlock?\n"
        "A deadlock is a situation where a set of processes are blocked because each process "
        "is holding a resource and waiting for another resource acquired by some other process.\n\n"
        "2. Necessary Conditions for Deadlock (Coffman Conditions):\n"
        "- Mutual Exclusion: At least one resource must be non-shareable.\n"
        "- Hold and Wait: A process must be holding at least one resource and waiting for additional resources.\n"
        "- No Preemption: Resources cannot be preempted; they are released only voluntarily.\n"
        "- Circular Wait: A set of processes waiting for each other in a circular chain.\n\n"
        "3. Deadlock Handling Strategies:\n"
        "- Deadlock Prevention: Invalidate one of the four necessary conditions.\n"
        "- Deadlock Avoidance: Use Banker's Algorithm to ensure the system is always in a safe state.\n"
        "- Deadlock Detection and Recovery: Allow deadlocks to occur, detect via Resource Allocation Graph, "
        "and recover via process termination or resource preemption.\n\n"
        "4. Critical Section Problem and Mutex:\n"
        "The critical section is the part of code where shared resources are accessed. "
        "Mutex (Mutual Exclusion Object) ensures only one thread accesses the critical section at a time."
    )

    page1.insert_text(fitz.Point(50, 70), sample_content, fontsize=11, fontname="helv", leading=16)
    path1 = os.path.join(output_dir, "short_notes.pdf")
    doc1.save(path1)
    doc1.close()
    print(" [Created] 1. short_notes.pdf (Valid typed digital notes)")

    # -------------------------------------------------------------
    # 2. Empty PDF (0 bytes)
    # -------------------------------------------------------------
    path2 = os.path.join(output_dir, "empty.pdf")
    with open(path2, "wb") as f:
        pass  # 0 bytes
    print(" [Created] 2. empty.pdf (0-byte empty file)")

    # -------------------------------------------------------------
    # 3. Scanned / Image-Only Dummy PDF (Drawing only, 0 extractable text)
    # -------------------------------------------------------------
    doc3 = fitz.open()
    page3 = doc3.new_page(width=595, height=842)
    
    # Draw vector rectangles and shapes to simulate an image/diagram page with no text
    shape = page3.new_shape()
    shape.draw_rect(fitz.Rect(50, 50, 545, 792))
    shape.finish(color=(0.2, 0.4, 0.8), fill=(0.95, 0.95, 0.95), width=2)
    shape.draw_circle(fitz.Point(297, 421), 100)
    shape.finish(color=(0.8, 0.2, 0.2), fill=(0.9, 0.8, 0.8), width=2)
    shape.commit()

    path3 = os.path.join(output_dir, "scanned_dummy.pdf")
    doc3.save(path3)
    doc3.close()
    print(" [Created] 3. scanned_dummy.pdf (Visual drawing with NO text layer)")

    print("\nAll 3 test sample PDFs are ready in 'test_samples/' folder!")


if __name__ == "__main__":
    create_samples()

