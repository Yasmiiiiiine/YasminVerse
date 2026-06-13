"""
CyberShield AI — Module d'analyse de sécurité
Évalue les mots de passe, les URL et les contenus d'e-mails suspects.
"""

from urllib.parse import urlparse
import re


def _get_risk_level(score: int) -> str:
    """Convertit un score numérique en niveau de risque textuel."""
    if score <= 25:
        return "Faible"
    if score <= 50:
        return "Modéré"
    if score <= 75:
        return "Élevé"
    return "Critique"


def _build_result(score: int, explanation: str) -> dict:
    """Construit le dictionnaire de résultat standardisé."""
    score = max(0, min(100, score))
    return {
        "risk_score": score,
        "risk_level": _get_risk_level(score),
        "explanation": explanation,
    }


def analyze_password(password: str) -> dict:
    """
    Évalue la force d'un mot de passe.
    Un score élevé indique un mot de passe faible (risque maximal = 100).
    """
    if not password:
        return _build_result(
            100,
            "Mot de passe vide : aucune protection. Choisissez immédiatement un mot de passe robuste.",
        )

    weaknesses = []
    score = 100

    length = len(password)

    if length >= 16:
        score -= 25
    elif length >= 12:
        score -= 15
    elif length >= 8:
        score -= 5
        weaknesses.append(f"longueur insuffisante ({length} caractères, minimum recommandé : 12)")
    else:
        weaknesses.append(f"longueur très faible ({length} caractères, minimum recommandé : 12)")

    has_upper = bool(re.search(r"[A-ZÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]", password))
    has_lower = bool(re.search(r"[a-zàâäéèêëïîôùûüÿç]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[^A-Za-zÀ-ÿ0-9]", password))

    if has_upper:
        score -= 15
    else:
        weaknesses.append("absence de lettres majuscules")

    if has_lower:
        score -= 15
    else:
        weaknesses.append("absence de lettres minuscules")

    if has_digit:
        score -= 15
    else:
        weaknesses.append("absence de chiffres")

    if has_special:
        score -= 15
    else:
        weaknesses.append("absence de caractères spéciaux (!@#$%…)")
    if re.fullmatch(r"(.)\1{3,}", password) or _is_common_pattern(password):
        score += 10
        weaknesses.append("motif répétitif ou prévisible détecté")

    if not weaknesses:
        explanation = (
            f"Mot de passe robuste ({length} caractères) avec majuscules, minuscules, "
            "chiffres et caractères spéciaux. Risque faible."
        )
    else:
        explanation = (
            "Points faibles détectés : " + ", ".join(weaknesses) + ". "
            "Renforcez votre mot de passe pour réduire le risque de compromission."
        )

    return _build_result(score, explanation)


def _is_common_pattern(password: str) -> bool:
    """Détecte des séquences triviales (123, abc, qwerty…)."""
    lowered = password.lower()
    common_sequences = ("123456", "abcdef", "qwerty", "password", "azerty", "000000")
    return any(seq in lowered for seq in common_sequences)


def analyze_url(url: str) -> dict:
    """
    Analyse sommaire d'une URL pour détecter des signes de phishing.
    Un score élevé indique une URL potentiellement malveillante.
    """
    if not url or not url.strip():
        return _build_result(100, "URL vide ou invalide : impossible d'évaluer la fiabilité.")

    url = url.strip()
    findings = []
    score = 0

    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "http://" + url

    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    full_lower = url.lower()

    if parsed.scheme.lower() != "https":
        score += 30
        findings.append("connexion non sécurisée (HTTP au lieu de HTTPS)")

    suspicious_keywords = (
        "secure", "bank", "login", "update", "verify", "account",
        "paypal", "wallet", "confirm", "support", "signin", "auth",
    )
    matched_keywords = [kw for kw in suspicious_keywords if kw in full_lower]
    if matched_keywords:
        score += min(30, len(matched_keywords) * 10)
        findings.append(
            "mots-clés suspects détectés : " + ", ".join(matched_keywords)
        )

    if hostname:
        subdomains = hostname.split(".")
        if len(subdomains) > 4:
            score += 20
            findings.append(
                f"nombre excessif de sous-domaines ({len(subdomains) - 2} sous-domaines)"
            )

        hyphen_count = hostname.count("-")
        if hyphen_count >= 3:
            score += 15
            findings.append(f"nom de domaine avec trop de tirets ({hyphen_count})")

        if re.search(r"\d{4,}", hostname):
            score += 10
            findings.append("nom de domaine contenant une longue séquence numérique")

        if hostname.replace(".", "").isdigit() or re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname):
            score += 15
            findings.append("URL basée sur une adresse IP (souvent utilisée en phishing)")

    if not findings:
        explanation = (
            f"URL « {url} » ne présente pas d'indicateurs évidents de phishing. "
            "Restez toutefois vigilant avant de saisir des informations sensibles."
        )
    else:
        explanation = (
            f"Analyse de l'URL « {url} » : " + "; ".join(findings) + ". "
            "Vérifiez l'expéditeur et l'authenticité du site avant toute action."
        )

    return _build_result(score, explanation)


def analyze_email_text(email_content: str) -> dict:
    """
    Analyse textuelle rapide pour détecter une tentative d'ingénierie sociale ou de phishing.
    Un score élevé indique un contenu potentiellement frauduleux.
    """
    if not email_content or not email_content.strip():
        return _build_result(
            0,
            "Contenu vide : aucun indicateur d'ingénierie sociale détecté.",
        )

    text_lower = email_content.lower()
    findings = []
    score = 0

    urgency_keywords = {
        "urgent": 15,
        "urgence": 15,
        "immédiat": 12,
        "immédiatement": 12,
        "bloqué": 15,
        "bloquee": 15,
        "suspendu": 12,
        "gagné": 18,
        "gagne": 18,
        "loterie": 15,
        "cliquez ici": 20,
        "cliquez": 10,
        "cliquer ici": 20,
        "facture impayée": 20,
        "facture impayee": 20,
        "impayée": 12,
        "impayee": 12,
        "compte compromis": 18,
        "vérifier votre compte": 15,
        "verifier votre compte": 15,
        "confirmer votre identité": 15,
        "action requise": 12,
        "dernier avertissement": 18,
        "mise à jour obligatoire": 12,
        "mise a jour obligatoire": 12,
        "mot de passe expiré": 15,
        "mot de passe expire": 15,
        "remboursement": 10,
        "héritage": 15,
        "heritage": 15,
        "bitcoin": 10,
        "crypto": 8,
    }

    for keyword, weight in urgency_keywords.items():
        if keyword in text_lower:
            score += weight
            findings.append(f"expression suspecte : « {keyword} »")

    if re.search(r"https?://[^\s]+", email_content, re.IGNORECASE):
        url_matches = re.findall(r"https?://[^\s]+", email_content, re.IGNORECASE)
        if len(url_matches) > 1:
            score += 10
            findings.append(f"plusieurs liens externes ({len(url_matches)})")

    if re.search(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", email_content):
        score += 15
        findings.append("demande potentielle de données bancaires (numéro de carte)")

    if text_lower.count("!") >= 3:
        score += 8
        findings.append("ton alarmiste (usage excessif de points d'exclamation)")

    if re.search(r"[A-ZÀ-ÖØ-Þ]{8,}", email_content):
        score += 8
        findings.append("texte en majuscules (technique de pression psychologique)")

    score = min(100, score)

    if not findings:
        explanation = (
            "Aucun indicateur majeur d'ingénierie sociale ou de phishing détecté dans ce message. "
            "Restez néanmoins prudent avec les pièces jointes et les liens inconnus."
        )
    else:
        explanation = (
            "Signes de tentative d'ingénierie sociale détectés : "
            + "; ".join(findings)
            + ". Ne cliquez pas sur les liens et ne communiquez aucune information personnelle."
        )

    return _build_result(score, explanation)


if __name__ == "__main__":
    import json

    print("=" * 60)
    print("  CyberShield AI — Analyseur de sécurité")
    print("=" * 60)

    examples = [
        ("Mot de passe faible", "analyze_password", "abc123"),
        ("Mot de passe fort", "analyze_password", "Tr0ub4dor&Secure!2024"),
        ("URL suspecte", "analyze_url", "http://secure-bank-login-update.example.com/auth"),
        ("URL normale", "analyze_url", "https://www.example.com/contact"),
        ("E-mail de phishing", "analyze_email_text",
         "URGENT ! Votre compte a été bloqué. Cliquez ici immédiatement "
         "pour éviter la suspension. Facture impayée en attente."),
        ("E-mail légitime", "analyze_email_text",
         "Bonjour, votre rendez-vous est confirmé pour mardi à 14h. Cordialement."),
    ]

    for label, func_name, input_value in examples:
        func = globals()[func_name]
        result = func(input_value)
        print(f"\n--- {label} ---")
        print(f"Entrée : {input_value[:80]}{'…' if len(input_value) > 80 else ''}")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
