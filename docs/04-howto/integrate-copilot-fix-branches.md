# How-To: Neue Requests auf Basis eines bestehenden Copilot-Fix-Branches erstellen

In diesem How-To erfährst du, wie du einen neuen Feature- oder Fix-Branch auf Basis eines bestehenden Copilot-Branches (z. B. `copilot/fix-xyz`) erzeugst. Das ist besonders sinnvoll, wenn du auf einem noch offenen Fix weitere Anforderungen oder Verbesserungen aufbauen möchtest, bevor alles nach `main` gemerged wurde.

---

## Schritt-für-Schritt-Anleitung

### 1. **Alle Änderungen vom Remote holen**

```bash
git fetch
```

Dadurch werden alle aktuellen Branches und Commits vom Remote-Repository geladen.

---

### 2. **Auf den bestehenden Copilot-Fix-Branch wechseln**

```bash
git checkout copilot/fix-xyz
```

Ersetze dabei `copilot/fix-xyz` durch den Branch-Namen des bestehenden Fixes, auf dem du aufbauen möchtest.

---

### 3. **Neuen Branch für deinen Request abzweigen**

```bash
git checkout -b feature/neues-feature
```

- Wähle einen sprechenden Namen für deinen neuen Branch (z. B. `feature/verbesserung-abc` oder `fix/neuer-bug`).
- Jetzt enthält dein neuer Branch alle Änderungen aus `copilot/fix-xyz`.

---

### 4. **Deine Änderungen umsetzen und committen**

Arbeite wie gewohnt und committe deine Änderungen:

```bash
git add .
git commit -m "Beschreibe deine Änderung"
```

---

### 5. **Branch zum Remote pushen**

```bash
git push -u origin feature/neues-feature
```

---

### 6. **Pull Request erstellen**

- Öffne auf GitHub einen neuen Pull Request von deinem neuen Branch auf den Ziel-Branch (meistens `main` oder ggf. direkt auf den ursprünglichen Copilot-Fix-Branch, wenn der Review gestaffelt erfolgen soll).

---

## **Tipp:**  
Wenn du mehrere Änderungen kombinieren willst (z. B. mehrere Copilot-Fixes), kannst du sie auch zusammenführen, indem du einen Branch in den anderen mergst (siehe [Merge-HowTo](./how-to-merge-copilot-fixes.md)).

---

## **Vorteile dieser Vorgehensweise**

- Du arbeitest immer auf dem aktuellsten Stand der noch nicht gemergten Änderungen.
- Du kannst beliebig viele Features oder Fixes aufeinander aufbauen, ohne warten zu müssen, bis alles in `main` gemerged ist.
- Konflikte werden frühzeitig erkannt und können direkt gelöst werden.

---

**Stand: September 2025**