# Tableau Dashboard Guide — UAV Unit Analytics Portfolio

Bu bələdçi 5 dashboard üçün hansı fayla qoşulacağını, hansı sahəni hansı
"shelf"-ə (Rows/Columns/Color/Size/Filter) qoyacağını addım-addım izah edir.

**Ümumi qeyd:** Sürətli/yüngül dashboardlar üçün `dash_*.csv` fayllarını
istifadə et (əvvəlcədən aqreqasiya olunub, Tableau-da sürətli yüklənir).
Daha dərin/granular analiz istəsən (məsələn atış növünə görə), xam
cədvəlləri (`shooting_performance.csv`, `flight_operations.csv`) birbaşa
qoşa bilərsən.

---

## Dashboard 1 — Bölmə Müqayisəsi (Department Comparison)
**Fayl:** `dash_department_scorecard.csv`

| Chart | Columns | Rows | Color | Növ |
|---|---|---|---|---|
| Uçuş saatı | department | total_flight_hours | department | Bar chart |
| Yanacaq səmərəliliyi | department | avg_fuel_burn_l_per_hour | avg_tech_condition (gradient) | Bar chart |
| Atış uğuru | department | avg_success_rate | department | Bar chart |
| Orta medal sayı | department | avg_medals | department | Bar chart |

**Addımlar:**
1. Connect → Text File → `dash_department_scorecard.csv`
2. Hər chart üçün: `department`-i **Columns**-a, müvafiq ölçünü **Rows**-a sürüklə → avtomatik bar chart yaranır
3. 4 chart-ı bir Dashboard-a (New Dashboard) yerləşdir, ölçüsü 2×2 grid
4. Bütün chart-ları eyni "department" filtrinə bağla (Use as Filter işarəsini aktivləşdir hər view-də) ki, birində bölmə seçəndə hamısı filtrlənsin

---

## Dashboard 2 — Uçuş və Yanacaq Analizi (Flight & Fuel Analysis)
**Fayllar:** `dash_monthly_flight_trend.csv` + `dash_department_scorecard.csv`

| Chart | Columns | Rows | Color | Növ |
|---|---|---|---|---|
| Mövsümilik | month | avg_flight_hours | — | Line chart |
| Bölmə üzrə yanacaq | department | avg_fuel_burn_l_per_hour | avg_tech_condition | Bar chart (aşağıdan yuxarı sırala) |

**Addımlar:**
1. `dash_monthly_flight_trend.csv`-i qoş → `month`-u Columns-a (Dimension kimi, **Continuous** et ki, xətt düzgün sıralansın), `avg_flight_hours`-u Rows-a → Line chart seç
2. Dərinlik istəsən: `fuel_consumption.csv`-i əlavə mənbə kimi qoş → `year`-i Columns-a, `total_fuel_liters`-i Rows-a, `department`-i Color-a → illər üzrə bölmə-bölmə böyümə xətti (2021→2026)

---

## Dashboard 3 — Atış Performansı (Shooting Performance)
**Fayl:** `shooting_performance.csv` (xam, atış-atış)

**Lazımi calculated field:**
```
Success Rate = COUNTD(IF [Outcome] = "Successful" THEN [Shot Id] END) / COUNTD([Shot Id])
```

| Chart | Columns | Rows | Color | Növ |
|---|---|---|---|---|
| Növə görə uğur | shot_type | Success Rate | shot_type | Bar chart |
| İlk atış effekti | is_first_shot | Success Rate | is_first_shot | Bar chart (2 sütun: TRUE/FALSE) |
| Zamanla trend | shot_date (YEAR) | Success Rate | — | Line chart |

**Addımlar:**
1. Connect → `shooting_performance.csv`
2. Analysis → Create Calculated Field → yuxarıdakı düsturu yaz → "Success Rate" adlandır
3. Hər 3 chart üçün müvafiq Dimension-u Columns-a, "Success Rate"-i Rows-a sürüklə
4. `is_first_shot` chart-ında fərqi vurğulamaq üçün Color-a da `is_first_shot` qoy — 61% vs 89% fərqi gözlə çarpacaq

---

## Dashboard 4 — Risk Göstəriciləri (Risk Indicators)
**Fayl:** `dash_risk_distribution.csv`

| Chart | Columns | Rows | Color | Növ |
|---|---|---|---|---|
| Paylanma | risk_score (bins, 10-luq) | CNT(person_id) | — | Histogram (Show Me → Histogram) |
| Bölmə üzrə orta risk | department | AVG(risk_score) | AVG(risk_score) gradient | Bar chart |
| İxtisaslaşma üzrə risk | specialization | AVG(risk_score) | AVG(risk_score) gradient | Bar chart (sıralanmış) |
| Ən riskli 20 nəfər | person_id (Top 20 filter, risk_score-a görə) | risk_score | risk_score (qırmızı-sarı-yaşıl) | Highlight table / Bar chart |

**Addımlar:**
1. Connect → `dash_risk_distribution.csv`
2. Histogram üçün: `risk_score`-u Columns-a sürükləyəndə Tableau avtomatik "bin" təklif edir (Show Me panelindən Histogram seç)
3. "Ən riskli 20" üçün: Filter → person_id → Top → By Field → Top 20 by SUM(risk_score)

---

## Dashboard 5 — Medal-Performans Uyğunsuzluğu (Medal-Performance Mismatch)
**Fayl:** `dash_medal_mismatch.csv`

| Chart | Columns | Rows | Color | Size | Növ |
|---|---|---|---|---|---|
| Əsas scatter | total_flight_hours | success_rate | medal_count | medal_count | Scatter plot |

**Addımlar:**
1. Connect → `dash_medal_mismatch.csv`
2. `total_flight_hours`-u Columns-a, `success_rate`-i Rows-a sürüklə → Tableau nöqtələr (scatter) göstərəcək
3. `medal_count`-u həm Color-a, həm Size-a sürüklə → az medal alan yüksək-performanslılar **kiçik/tünd nöqtə kimi sağ-yuxarı küncdə** görünəcək (məhz axtardığın uyğunsuzluq!)
4. Sağ-yuxarı küncdəki (yüksək saat + yüksək uğur) kiçik/tünd nöqtələrin üzərinə hover et → `person_id`-ni gör
5. İstəsən, Reference Line əlavə et (Analytics panel → Median Line hər iki ox üçün) ki, 4 kvadrant yaransın: "yüksək performans/aşağı medal" kvadrantı ən vacib olanıdır

---

## Bütün 5 dashboard-ı bir Story-yə birləşdirmək
Tableau-da **Story** funksiyasından istifadə et (File → New Story) — 5 dashboard-ı ardıcıl "səhifə" kimi düz, hər birinin altına 1 cümləlik tapıntı yaz (məs. "Delta bölməsi ən çox medal verir, amma performans göstəriciləri ortadan aşağıdır"). Bu, portfolio təqdimatını README-dən daha canlı edir.
