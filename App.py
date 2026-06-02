import streamlit as st
import pickle
import numpy as np
import pandas as pd
import requests

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PCOS Health Advisor",
    page_icon="🌸",
    layout="wide"
)

# ─── Load Model ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    with open('pcos_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('feature_columns.pkl', 'rb') as f:
        features = pickle.load(f)
    return model, features

model, feature_columns = load_model()

# ─── Food Recommendation Logic ───────────────────────────────────────────────
def get_food_recommendations(risk_level, fast_food, hair_growth, bmi, cycle_length):
    recommendations = {
        "eat": [],
        "avoid": [],
        "meal_plan": []
    }

    # Base recommendations for all PCOS risk levels
    if risk_level == "High":
        recommendations["eat"] = [
            "🥦 Leafy greens (spinach, kale) — reduce inflammation & insulin resistance",
            "🫐 Berries (blueberries, strawberries) — low glycemic, antioxidant-rich",
            "🐟 Fatty fish (salmon, sardines) — omega-3s reduce androgen levels",
            "🥑 Avocado — healthy fats balance hormones",
            "🌱 Flaxseeds — lignans lower excess androgens (great for hair growth)",
            "🍵 Spearmint tea — shown to reduce testosterone in women with PCOS",
            "🥚 Eggs — high protein, keeps blood sugar stable",
            "🌾 Quinoa & brown rice — low-GI complex carbs",
            "🥜 Walnuts & almonds — reduce inflammation",
            "🫘 Lentils & chickpeas — high fiber, low glycemic index"
        ]
        recommendations["avoid"] = [
            "🚫 White bread, white rice, pasta — spike blood sugar",
            "🚫 Sugary drinks (soda, juice) — worsen insulin resistance",
            "🚫 Processed snacks & fast food — inflammatory",
            "🚫 Dairy milk — may increase androgen levels",
            "🚫 Red meat — increases inflammation",
            "🚫 Alcohol — disrupts hormone balance",
            "🚫 Soy products in excess — phytoestrogens",
            "🚫 Refined sugars & desserts"
        ]
        recommendations["meal_plan"] = [
            "**Day 1:** Oatmeal + berries (breakfast) | Quinoa salad + grilled salmon (lunch) | Stir-fried tofu + vegetables (dinner)",
            "**Day 2:** Avocado toast on whole grain + spearmint tea (breakfast) | Lentil soup + whole grain bread (lunch) | Baked salmon + roasted broccoli (dinner)",
            "**Day 3:** Greek yogurt + flaxseeds + walnuts (breakfast) | Chickpea salad + olive oil dressing (lunch) | Grilled chicken + sweet potato + greens (dinner)"
        ]

    elif risk_level == "Moderate":
        recommendations["eat"] = [
            "🥦 Cruciferous vegetables (broccoli, cauliflower) — hormone detox support",
            "🍓 Low-GI fruits (berries, apple, pear)",
            "🥚 Eggs & lean protein — stabilize blood sugar",
            "🌾 Whole grains (oats, quinoa, millet)",
            "🫘 Legumes (lentils, beans) — fiber-rich",
            "🥜 Nuts & seeds — healthy fats",
            "🫐 Anti-inflammatory spices (turmeric, cinnamon)",
            "🍵 Green tea — improves insulin sensitivity"
        ]
        recommendations["avoid"] = [
            "⚠️ Limit white rice & refined carbs",
            "⚠️ Limit dairy — try almond or oat milk instead",
            "⚠️ Reduce sugar intake",
            "⚠️ Minimize fast food & fried items",
            "⚠️ Avoid skipping meals — causes blood sugar spikes"
        ]
        recommendations["meal_plan"] = [
            "**Day 1:** Oats + cinnamon + banana (breakfast) | Brown rice + dal + salad (lunch) | Grilled fish + steamed vegetables (dinner)",
            "**Day 2:** Smoothie with spinach, berries, almond milk (breakfast) | Whole wheat wrap + hummus + veggies (lunch) | Stir-fried tofu + quinoa (dinner)",
            "**Day 3:** Whole grain toast + peanut butter + apple (breakfast) | Lentil soup + multigrain bread (lunch) | Chicken breast + roasted sweet potato (dinner)"
        ]

    else:  # Low risk
        recommendations["eat"] = [
            "✅ Balanced diet with plenty of vegetables",
            "✅ Whole grains over refined grains",
            "✅ Lean proteins (chicken, fish, eggs, legumes)",
            "✅ Healthy fats (olive oil, avocado, nuts)",
            "✅ Stay hydrated — 8+ glasses of water daily",
            "✅ Include anti-inflammatory foods regularly"
        ]
        recommendations["avoid"] = [
            "💡 Minimize ultra-processed foods",
            "💡 Watch sugar intake",
            "💡 Limit alcohol"
        ]
        recommendations["meal_plan"] = [
            "**Day 1:** Yogurt parfait + granola + fruits (breakfast) | Grilled chicken salad (lunch) | Salmon + vegetables + brown rice (dinner)",
            "**Day 2:** Smoothie bowl + seeds (breakfast) | Veggie wrap + hummus (lunch) | Dal + roti + salad (dinner)",
            "**Day 3:** Eggs + whole grain toast + avocado (breakfast) | Quinoa bowl + roasted veggies (lunch) | Grilled fish + sweet potato (dinner)"
        ]

    # Additional recommendations based on symptoms
    extra = []
    if hair_growth == 1:
        extra.append("💡 **For hair growth (excess androgens):** Add spearmint tea (2 cups/day) and flaxseeds (2 tbsp/day) — both shown to reduce testosterone levels")
    if fast_food == 1:
        extra.append("💡 **To replace fast food:** Try air-fried snacks, roasted chickpeas, or homemade wraps — same satisfaction, no insulin spike")
    if bmi > 25:
        extra.append("💡 **For weight management:** Focus on protein + fiber at every meal to reduce cravings and improve insulin sensitivity")
    if cycle_length > 35:
        extra.append("💡 **For irregular cycles:** Vitamin D, magnesium, and omega-3 rich foods support hormonal regulation")

    return recommendations, extra


# ─── USDA Food Data API ──────────────────────────────────────────────────────
def fetch_nutrition(food_name, api_key):
    try:
        url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&pageSize=1&api_key={api_key}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get('foods'):
            food = data['foods'][0]
            nutrients = {n['nutrientName']: n['value'] for n in food.get('foodNutrients', [])}
            return {
                'name': food.get('description', food_name),
                'calories': nutrients.get('Energy', 'N/A'),
                'protein': nutrients.get('Protein', 'N/A'),
                'fiber': nutrients.get('Fiber, total dietary', 'N/A'),
                'sugar': nutrients.get('Sugars, total including NLEA', 'N/A')
            }
    except:
        return None


# ─── UI ─────────────────────────────────────────────────────────────────────
st.title("🌸 PCOS Health Advisor")
st.markdown("#### Predict your PCOS risk and get personalized nutrition recommendations")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Your Health Information")

    st.markdown("**Basic Info**")
    age = st.slider("Age (years)", 18, 50, 28)
    weight = st.number_input("Weight (Kg)", 30.0, 120.0, 60.0)
    height = st.number_input("Height (Cm)", 140.0, 190.0, 160.0)
    bmi = round(weight / ((height / 100) ** 2), 2)
    st.info(f"Your BMI: **{bmi}** ({'Normal' if bmi < 25 else 'Overweight' if bmi < 30 else 'Obese'})")

    st.markdown("**Cycle & Vitals**")
    cycle_ri = st.selectbox("Menstrual Cycle", [("Regular (R)", 4), ("Irregular (I)", 5)], format_func=lambda x: x[0])
    cycle_length = st.slider("Cycle Length (days)", 21, 60, 30)
    pulse_rate = st.slider("Pulse Rate (bpm)", 50, 100, 72)
    rr = st.slider("Breathing Rate (breaths/min)", 12, 25, 18)
    hb = st.number_input("Hemoglobin Hb (g/dl)", 8.0, 18.0, 13.0)

with col2:
    st.subheader("🔬 Symptoms & Lifestyle")

    st.markdown("**Symptoms (Yes=1, No=0)**")
    hair_growth = st.selectbox("Excess Hair Growth (Hirsutism)", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    skin_darkening = st.selectbox("Skin Darkening", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    hair_loss = st.selectbox("Hair Loss / Thinning", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    pimples = st.selectbox("Pimples / Acne", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    fast_food = st.selectbox("Regular Fast Food Consumer", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    reg_exercise = st.selectbox("Regular Exercise", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    pregnant = st.selectbox("Currently Pregnant", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")

    st.markdown("**Ultrasound Results (if available)**")
    follicle_l = st.slider("Follicle Count Left Ovary", 0, 20, 5)
    follicle_r = st.slider("Follicle Count Right Ovary", 0, 20, 5)
    endometrium = st.number_input("Endometrium Thickness (mm)", 0.0, 20.0, 7.0)

    st.markdown("**Blood Work (if available)**")
    blood_group = st.selectbox("Blood Group", [11, 12, 13, 14, 15, 16, 17, 18],
                                format_func=lambda x: {11:"A+",12:"A-",13:"B+",14:"B-",15:"O+",16:"O-",17:"AB+",18:"AB-"}[x])
    marriage_yrs = st.number_input("Years Married (0 if not)", 0, 20, 0)


# ─── Prediction ─────────────────────────────────────────────────────────────
st.markdown("---")

# Optional USDA API
with st.expander("🔑 Optional: Add USDA API Key for live nutrition data"):
    usda_key = st.text_input("USDA API Key", type="password", placeholder="Paste your key here")

if st.button("🔍 Analyze My PCOS Risk", use_container_width=True, type="primary"):

    # Build input — fill all 42 features with defaults, override with user inputs
    input_dict = {col: 0 for col in feature_columns}

    input_dict['Age (yrs)'] = age
    input_dict['Weight (Kg)'] = weight
    input_dict['Height(Cm)'] = height
    input_dict['BMI'] = bmi
    input_dict['Blood Group'] = blood_group
    input_dict['Pulse rate(bpm)'] = pulse_rate
    input_dict['RR (breaths/min)'] = rr
    input_dict['Hb(g/dl)'] = hb
    input_dict['Cycle(R/I)'] = cycle_ri[1]
    input_dict['Cycle length(days)'] = cycle_length
    input_dict['Marraige Status (Yrs)'] = marriage_yrs
    input_dict['Pregnant(Y/N)'] = pregnant
    input_dict['hair growth(Y/N)'] = hair_growth
    input_dict['Skin darkening (Y/N)'] = skin_darkening
    input_dict['Hair loss(Y/N)'] = hair_loss
    input_dict['Pimples(Y/N)'] = pimples
    input_dict['Fast food (Y/N)'] = fast_food
    input_dict['Reg.Exercise(Y/N)'] = reg_exercise
    input_dict['Follicle No. (L)'] = follicle_l
    input_dict['Follicle No. (R)'] = follicle_r
    input_dict['Endometrium (mm)'] = endometrium

    input_df = pd.DataFrame([input_dict])[feature_columns]
    prob = model.predict_proba(input_df)[0][1]

    if prob >= 0.65:
        risk_level = "High"
        color = "#E91E63"
        emoji = "🔴"
    elif prob >= 0.35:
        risk_level = "Moderate"
        color = "#FF9800"
        emoji = "🟡"
    else:
        risk_level = "Low"
        color = "#4CAF50"
        emoji = "🟢"

    # Results
    color_map = {"High": "red", "Moderate": "orange", "Low": "green"}
    st.markdown(f"## {emoji} PCOS Risk Level: **:{color_map[risk_level]}[{risk_level}]**")
    st.progress(float(prob))
    st.markdown(f"**Model Confidence: {prob:.1%}**")

    st.markdown("> ⚠️ *This tool is for informational purposes only. Always consult a healthcare professional for diagnosis.*")
    st.markdown("---")

    # Food Recommendations
    recs, extra_tips = get_food_recommendations(risk_level, fast_food, hair_growth, bmi, cycle_length)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### ✅ Foods to Eat")
        for food in recs["eat"]:
            st.markdown(food)

    with col_b:
        st.markdown("### ❌ Foods to Avoid")
        for food in recs["avoid"]:
            st.markdown(food)

    if extra_tips:
        st.markdown("### 💡 Personalized Tips")
        for tip in extra_tips:
            st.markdown(tip)

    st.markdown("### 📅 3-Day Sample Meal Plan")
    for day in recs["meal_plan"]:
        st.markdown(day)

    # Live nutrition data if API key provided
    if usda_key:
        st.markdown("### 🔬 Live Nutrition Data (USDA)")
        lookup_foods = ["blueberries", "salmon", "quinoa", "spinach", "flaxseed"]
        cols = st.columns(len(lookup_foods))
        for i, food in enumerate(lookup_foods):
            data = fetch_nutrition(food, usda_key)
            if data:
                with cols[i]:
                    st.metric(data['name'][:15], f"{data['calories']} kcal")
                    st.caption(f"Protein: {data['protein']}g | Fiber: {data['fiber']}g")

st.markdown("---")
st.caption("Built by Hemasree Chilamkurthy | MS Computer Science, UAB | Data Science & ML Portfolio Project")