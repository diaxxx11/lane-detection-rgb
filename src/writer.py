# src/writer.py
from src import config

def write_sections(sections):
    """
    sections: list of dicts with 'start', 'end', 'tags'
    Writes a text file in the format:
    # [[section]]
    # start = <ms>
    # tags = [...]
    # end = <ms>
    """
    out_path = config.OUTPUT_FILE
    with open(out_path, "w") as f:
        for sec in sections:
            f.write("# [[section]]\n")
            f.write(f"# start = {sec['start']}\n")
            f.write(f"# tags = {sec['tags']}\n")
            f.write(f"# end = {sec['end']}\n\n")
    print(f"Sections written to {out_path}")
