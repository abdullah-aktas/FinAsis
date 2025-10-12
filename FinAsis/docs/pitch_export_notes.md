# Pitch Export – PDF/Slide Alma Notları (Windows)

Seçenek 1 – VS Code: Markdown PDF eklentisi
1) VS Code Marketplace’ten “Markdown PDF” kurun.
2) `FinAsis_Investor_Deck_TR.md` dosyasını açın.
3) Sağ tık → “Markdown PDF: Export (pdf)” seçin.

Seçenek 2 – Pandoc (PDF veya PPTX)
- Önce Pandoc ve LaTeX (PDF için) veya yalnızca Pandoc (PPTX için) kurun.
- PowerShell (örnek):
```powershell
# PDF (wkhtmltopdf veya LaTeX kurulu olmalı)
pandoc FinAsis_Investor_Deck_TR.md -o FinAsis_Investor_Deck_TR.pdf --pdf-engine=xelatex

# PowerPoint (PPTX) çıktısı
pandoc FinAsis_Investor_Deck_TR.md -o FinAsis_Investor_Deck_TR.pptx -t pptx
```

İpucu
- Başlıklara (##) slide dönüşümü için Pandoc ile `-t pptx` kullanabilirsiniz; her H1/H2 yeni slayt olarak işlenir.
- Görseller eklemek isterseniz: `docs/static/` altına kaydedip Markdown içinde referanslayın.
