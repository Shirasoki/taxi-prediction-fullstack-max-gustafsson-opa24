# taxi-prediction-fullstack-max-gustafsson-opa24
Lab 1, building a fullstack application for taxi prediction.


# 🚕 Taxi Fare Prediction

Ett enkelt fullstack-projekt som förutspår taxipriser baserat på kördata.  
Projektet är byggt i **Python**, med **FastAPI** som backend, **Streamlit** som frontend och en tränad **Random Forest-modell** i scikit-learn.

---

## 🧠 Funktioner

- **Prediktion av taxipris** utifrån distans, tid och tariffer.  
- **Två användarlägen**:
  - **AI-sök:** användaren anger start och slutadress, modellen får distans och tid via Gemini API.  
  - **Manuellt läge:** användaren matar själv in värden som distans, minuter, och tariffer.  
- **Random Forest-modell** tränad på rensad CSV-data med borttagna outliers.  

---

## 🧩 Teknisk struktur

src/
├── taxipred/
│ ├── backend/
│ │ ├── api.py # FastAPI med /taxi/predict endpoint
│ │ └── data_processing.py # Datamodeller (Pydantic) och datahantering
│ ├── utils/
│ │ ├── helpers.py # API-anrop till backend
│ │ └── constants.py # Filvägar till data och modeller
│ ├── data/ # Rå och rensad data (CSV)
│ └── app.py # Streamlit-dashboard


📊 Modell

Modellen tränades med Random Forest Regressor på en rensad dataset (cleaned_data_v2.csv).
Förbehandling:

borttagning av null-värden

beräkning av saknade fält via formel

borttagning av outliers (1–99%)

Resultat: 

Mean Absolute Error: 1.30
Mean Squared Error: 3.36
R2 Score: 0.9959


