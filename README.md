# 📁 P12 – Développez une architecture back-end sécurisée avec Python et SQL

## 🧩 Développement d'une solution CRM

Projet réalisé dans le cadre du parcours **Développeur d'application Python** chez OpenClassrooms.

---

## ✅ Prérequis

- Un IDE comme **VSCode**, **PyCharm**, etc.
- **Python** : [https://www.python.org/](https://www.python.org/)
- **MySQL** : [https://www.mysql.com/](https://www.mysql.com/)

---

## ⚙️ Installation sous Windows

1. **Cloner le repository**  
```bash
git clone https://github.com/Laysi88/P12
```
2. **Créer un envirronement virtuel**  
```bash
python -m venv env 
 ```

3. **Activer l'environnement virtuel**
```powershell
.\env\Scripts\Activate.ps1
```
4. **Installer les dépendances**
```bash
pip install -r requirements.txt
``` 
5. **Créer un fichier `.env`** à la racine du projet avec les variables suivantes :
```env
DATABASE_URL="mysql+mysqlconnector://<nom_utilisateur>:<mot_de_passe>@localhost/<nom_base_de_donnees>"
SECRET_KEY=<Clé d'encryptage des mots de passe>
SENTRY=<Votre DNS Sentry>
```

## Lancement de l'application ##
Au premier démarrage de l'application vous pourrez peupler la BDD avec les roles et un utilisateur administrateur par défaut avec la commande:
```bash
python main.py
```

Ensuite vous pourrez vous connecter en utilisant:
```bash
python main.py login
``` 
Avec les identifiants:
```yaml
Email : admin@admin.com  
Mot de passe : admin123
```

Relancer l'application avec:
```bash
python main.py
```

 Vous pouvez désormais utiliser le CRM