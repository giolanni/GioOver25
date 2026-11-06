"""Short, static descriptions for report engines; no runtime text generation.

Descriptions are informational only; never change scoring or selection.
"""
DESCRIPTIONS = {
    "v1": "Prima versione del modello Over 2.5.",
    "v13": "Modello Over 2.5 della famiglia V13.",
    "v20": "Modello Over 2.5 originale V20, invariato.",
    "v20plus": "V20 ALTA e MEDIA-ALTA promosse con conferma V22/V25.",
    "v20select": "Solo MEDIA-ALTA V20 selezionate con conferma V22/V25.",
    "v20def": "V20 con penalizzazione delle difese forti.",
    "v20defselect": "Sottoinsieme selezionato della famiglia V20 strong-defense.",
    "v20defplus": "V20 strong-defense con selezioni aggiuntive confermate.",
    "v20defplus_v2": "Seconda variante delle promozioni V20 strong-defense.",
    "v20defplus_v3": "V20def ALTA e promozioni con soglie 69/60/80.",
    "v21": "Modello Over 2.5 della famiglia V21.",
    "v21dev": "Variante sperimentale selettiva della famiglia V21.",
    "v22": "Modello Over 2.5 della famiglia V22.",
    "v22def": "V22 con penalizzazione delle difese forti.",
    "v23": "Modello Over 2.5 della famiglia V23.",
    "v24": "Modello Over 2.5 della famiglia V24.",
    "v25": "Modello Over 2.5 della famiglia V25.",
    "v25def": "V25 con penalizzazione delle difese forti.",
    "v251": "Variante V25.1 del modello Over 2.5.",
    "v26": "Modello Over 2.5 della famiglia V26.",
    "v26def": "V26 con penalizzazione delle difese forti.",
    "v27": "Modello sperimentale Over 2.5 V27.",
    "v30": "Modello Over 2.5 per campioni con storico giovane.",
    "v31": "Modello Over 2.5 per campioni con storico giovane.",
    "vg1": "Modello BTTS originale, fasce native invariate.",
    "vg1.2": "BTTS score 65-<70, escluse le ALTA gia' in VG1.",
    "vg1.3": "BTTS score 68-<72, escluse le ALTA gia' in VG1.",
    "vg1.4": "BTTS score 65-<72, escluse le ALTA gia' in VG1.",
    "vg2.2": "Variante BTTS VG1 con MinGFL5 >= 2.2.",
    "vg2.6": "Variante BTTS VG1 con MinGFL5 >= 2.6.",
    "veg90": "Selezione sperimentale Over 2.5 basata su expected goals.",
}

def description(engine: str) -> str:
    return DESCRIPTIONS.get(str(engine).lower(), "Modello Over 2.5; dettagli non censiti.")
