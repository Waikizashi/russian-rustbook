#!/usr/bin/env python3
"""Optional PDF export from the same validated EPUB, using PyMuPDF."""
from pathlib import Path
import json
import fitz
from book_config import NAME, PUBLICATION

ROOT = Path(__file__).resolve().parents[1]


def main():
    upstream = json.loads((ROOT / "upstream.json").read_text())
    source = fitz.open(ROOT / "downloads" / (NAME + ".epub"))
    source.layout(width=600, height=850, fontsize=12)
    pdf = fitz.open("pdf", source.convert_to_pdf())
    pdf.set_metadata({
        "title":PUBLICATION["title"],
        "author":"; ".join(PUBLICATION["authors"]),
        "subject":"Полная русская версия; Rust "+upstream["rust"]+", edition "+upstream["edition"],
        "creator":"Russian Rustbook",
    })
    pdf.set_toc(source.get_toc())
    links, unresolved = 0, []
    for i in range(len(source)):
        for original in source[i].get_links():
            link = {k:v for k,v in original.items() if k not in ["xref","id"]}
            if original["kind"] == fitz.LINK_NAMED:
                uri = original.get("nameddest") or original.get("name") or original.get("uri")
                destination = source.resolve_link(uri)
                if not destination or destination[0] < 0:
                    unresolved.append(str(original))
                    continue
                link = {"kind":fitz.LINK_GOTO,"from":original["from"],"page":destination[0],"to":fitz.Point(destination[1],destination[2])}
            elif original["kind"] == fitz.LINK_GOTO and isinstance(original.get("page"),tuple):
                link["page"] = source.page_number_from_location(original["page"])
            if link["kind"] in [fitz.LINK_GOTO,fitz.LINK_URI]:
                pdf[i].insert_link(link)
                links += 1
        pdf[i].insert_text((291,830),str(i+1),fontsize=8,fontname="helv",color=(.4,.4,.4))
    assert not unresolved, unresolved
    path = ROOT / "downloads" / (NAME + ".pdf")
    pdf.save(path,garbage=4,deflate=True)
    reopened = fitz.open(path)
    outside = []
    for index,page in enumerate(reopened):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines",[]):
                for span in line["spans"]:
                    r = fitz.Rect(span["bbox"])
                    if r.x0 < -1 or r.y0 < -1 or r.x1 > page.rect.width+1 or r.y1 > page.rect.height+1:
                        outside.append((index+1,span["text"]))
    assert not outside, outside
    previews = ROOT / "dist/pdf-preview"
    previews.mkdir(parents=True,exist_ok=True)
    selected = sorted({0,1,20,len(reopened)//2,len(reopened)-1})
    for index in selected:
        reopened[index].get_pixmap(matrix=fitz.Matrix(1,1)).save(previews/f"page-{index+1:03d}.png")
    report = {"pages":len(reopened),"toc_entries":len(reopened.get_toc()),"links":links,"unresolved_links":unresolved,"text_outside_page":outside,"preview_pages":[i+1 for i in selected]}
    (ROOT/"dist/pdf-verification.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False))


if __name__ == "__main__":
    main()
