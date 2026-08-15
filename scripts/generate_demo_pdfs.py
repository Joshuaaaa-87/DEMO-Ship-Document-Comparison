"""Create two clearly fictional six-page maintenance manuals for the demo."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "demo"

COMMON_PAGES = [
    ("1. 文件識別與適用範圍", [
        "文件名稱：Main Engine Cooling System Maintenance Procedure",
        "適用設備：主機冷卻系統、循環泵浦與溫度感測器。",
        "本文件為虛構 Demo 資料，不得用於真實船舶操作。",
    ]),
    ("2. 安全準備", [
        "維修前應確認主機停止、隔離電源，並穿戴防護裝備。",
        "任何警告標示不清楚時，應停止作業並通知工程主管。",
    ]),
]

V10_PAGES = [
    ("3. 冷卻溫度檢查", [
        "2.1 冷卻液出口溫度建議維持在 85°C 以下。",
        "工程人員應每月檢查一次溫度感測器讀值。",
        "超過建議值時，記錄於維修日誌。",
    ]),
    ("4. 循環泵浦保養", [
        "使用零件料號 CP-100 的密封件。",
        "啟動前建議檢查循環泵浦是否有洩漏。",
        "適用船型：巡防艦 A 型。",
    ]),
    ("5. 停機程序", [
        "先停止循環泵浦，再關閉冷卻液出口閥。",
        "如發現壓力高於 10 bar，請記錄並通報。",
    ]),
    ("6. 維修紀錄", [
        "維修完成後，由工程人員填寫維修日誌。",
        "保留最近一次檢查結果即可。",
    ]),
]

V11_PAGES = [
    ("3. 冷卻溫度檢查", [
        "2.1 冷卻液出口溫度必須維持在 80°C 以下。",
        "工程人員必須每週檢查一次溫度感測器讀值。",
        "超過限值時，應立即停止主機並通知工程主管。",
    ]),
    ("4. 循環泵浦保養", [
        "使用零件料號 CP-120 的耐熱密封件。",
        "每次啟動前必須檢查循環泵浦是否有洩漏。",
        "適用船型：巡防艦 A 型及 B 型。",
    ]),
    ("5. 停機程序", [
        "先關閉冷卻液出口閥，再停止循環泵浦。",
        "如發現壓力高於 8 bar，必須停止作業並通報。",
    ]),
    ("6. 維修紀錄", [
        "維修完成後，由工程人員填寫維修日誌與驗證紀錄。",
        "保留最近三次檢查結果，供安全品質人員覆核。",
    ]),
]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#607276"))
    canvas.drawString(18 * mm, 12 * mm, "Fictional training data - not an operational instruction")
    canvas.drawRightString(192 * mm, 12 * mm, f"PDF p.{doc.page}")
    canvas.restoreState()


def build(version: str, pages: list[tuple[str, list[str]]], filename: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(OUTPUT_DIR / filename), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm)
    styles = getSampleStyleSheet()
    story = []
    for idx, (heading, lines) in enumerate(COMMON_PAGES + pages, start=1):
        story.append(Paragraph("AI Ship Document Comparison Demo", styles["Title"]))
        story.append(Spacer(1, 6 * mm))
        story.append(Paragraph(f"Version: {version} | Issue date: 2026-08-15", styles["Heading2"]))
        story.append(Spacer(1, 5 * mm))
        story.append(Paragraph(heading, styles["Heading1"]))
        story.append(Spacer(1, 3 * mm))
        for line in lines:
            story.append(Paragraph(line, styles["BodyText"]))
            story.append(Spacer(1, 3 * mm))
        if idx == 4:
            table = Table([["檢查項目", "舊/新要求"], ["冷卻液溫度", lines[0]], ["檢查頻率", lines[1]]], colWidths=[42 * mm, 120 * mm])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#159B91")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E5E3")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]))
            story.extend([Spacer(1, 5 * mm), table])
        if idx < 6:
            story.append(PageBreak())
    document.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build("v1.0", V10_PAGES, "Main_Engine_Cooling_v1.0.pdf")
    build("v1.1", V11_PAGES, "Main_Engine_Cooling_v1.1.pdf")
    print(f"Created demo PDFs in {OUTPUT_DIR}")

