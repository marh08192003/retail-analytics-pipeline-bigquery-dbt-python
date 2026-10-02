import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#Cargar el archivo Excel 
path = r"Online Retail.xlsx"
df = pd.read_excel(path)

#Inspeccionar estructura y nulos
print("Informacion General")
print(df.info())

print("Conteo de nulos")
print(df.isnull().sum())

print("Muestra de datos")
print(df.head())

#Filas iniciales
print(f"Filas iniciales: {len(df)}")

#Eliminacion de nulos en Customer ID
df_clean = df.dropna(subset=['CustomerID']).copy()

#Convertir CustomerID a entero
df_clean['CustomerID'] = df_clean['CustomerID'].astype(int)

#Filtarr solo transacciones validas (cantidad y precio positivo)
df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['UnitPrice']> 0)]

#Eliminar filas duplicadas
df_clean = df_clean.drop_duplicates()

#Asegurar formato datetime en la fecha
df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])

print(f"Filas tras la limpieza: {len(df_clean)}")
print("\nMuestra de datos limpios:")
print(df_clean.head())

# ==========================================
# CONSTRUCCIÓN DE COHORTES Y RETENCIÓN
# ==========================================

print(' =========================================== ')
print(' CONSTRUCCIÓN DE COHORTES Y RETENCIÓN ')
print(' =========================================== ')

#Obtener el mes de cafa transaccion (formato period o inicio de mes)
def get_month(x):
    return pd.Timestamp(x.year, x.month, 1)

df_clean['InvoiceMonth'] = df_clean['InvoiceDate'].apply(get_month)

#Obtener el mes de la 1ra compra de cada cliente
df_clean['CohortMonth'] = df_clean.groupby('CustomerID')['InvoiceMonth'].transform('min')

#Calcular la diferencia en meses
def get_date_int(df, column):
    year = df[column].dt.year
    month = df[column].dt.month
    return year, month

invoice_year, invoice_month = get_date_int(df_clean, 'InvoiceMonth')
cohort_year, cohort_month = get_date_int(df_clean, 'CohortMonth')

years_diff = invoice_year - cohort_year
months_diff = invoice_month - cohort_month

#CohortIndex: 0 es el mes inicial del cohorte
df_clean['CohortIndex'] = years_diff* 12 + months_diff

#Agrupar por cohorte y cohortindex para contar clientes unicos
cohort_data = df_clean.groupby(['CohortMonth', 'CohortIndex'])['CustomerID'].nunique().reset_index()

#Crear tabla pivote de cliente retenidos
cohort_counts = cohort_data.pivot(index='CohortMonth', columns='CohortIndex', values='CustomerID')

#Calcular el porcentaje de retnecion
cohort_sizes = cohort_counts.iloc[:, 0]  # Clientes en el mes 0
retention = cohort_counts.divide(cohort_sizes, axis=0) * 100

print("\n--- MATRIZ DE RETENCIÓN (%) ---")
print(retention.round(1))

# ==========================================
# GENERACIÓN DE GRÁFICA (HEATMAP)
# ==========================================

print(' ============================================ ')
print(' GENERACIÓN DE GRÁFICA (HEATMAP) ')
print(' ============================================ ')

plt.figure(figsize=(14, 8))
plt.title('Matriz de Retención por Cohorte (%) - Online Retail', fontsize=14, fontweight='bold')

# Dar formato de cadena AAAA-MM a las filas para la gráfica
retention_df = retention.round(1)
retention_df.index = retention_df.index.strftime('%Y-%m')

sns.heatmap(
    data=retention_df,
    annot=True,
    fmt='.1f',
    cmap='Blues',
    vmin=0,
    vmax=50,
    cbar_kws={'label': 'Porcentaje de Retención (%)'}
)

plt.xlabel('Meses transcurridos desde la 1ª compra (Cohort Index)', fontsize=11)
plt.ylabel('Mes de Adquisición (Cohorte)', fontsize=11)
plt.tight_layout()

# Guardar la imagen en tu carpeta
plt.savefig('matriz_retencion.png', dpi=300)
print("\n[OK] Gráfica guardada exitosamente como 'matriz_retencion.png'")

# ==========================================
# CÁLCULO DE LTV SIMPLE POR COHORTE
# ==========================================

print(' ========================================== ')
print(' CÁLCULO DE LTV SIMPLE POR COHORTE ')
print(' ========================================== ')

# 1. Crear la columna de Ingresos Totales por fila
df_clean['TotalSum'] = df_clean['Quantity'] * df_clean['UnitPrice']

# 2. Calcular la fecha de la primera y última compra por cliente
customer_lifespan = df_clean.groupby('CustomerID').agg(
    FirstPurchase=('InvoiceDate', 'min'),
    LastPurchase=('InvoiceDate', 'max')
)

# Diferencia en meses (+1 para que el mes inicial cuente como 1)
customer_lifespan['LifespanMonths'] = (
    (customer_lifespan['LastPurchase'].dt.year - customer_lifespan['FirstPurchase'].dt.year) * 12 +
    (customer_lifespan['LastPurchase'].dt.month - customer_lifespan['FirstPurchase'].dt.month) + 1
)

# Asociar la vida útil de vuelta
df_clean = df_clean.drop(columns=['LifespanMonths'], errors='ignore')
df_clean = df_clean.merge(customer_lifespan[['LifespanMonths']], on='CustomerID', how='left')

# 3. Métricas agrupadas por Cohorte
ltv_by_cohort = df_clean.groupby('CohortMonth').agg(
    TotalRevenue=('TotalSum', 'sum'),
    TotalOrders=('InvoiceNo', 'nunique'),
    TotalCustomers=('CustomerID', 'nunique'),
    AvgLifespanMonths=('LifespanMonths', 'mean')
).reset_index()

# 4. Fórmulas de LTV por Cliente Promedio
# AOV: Ticket Promedio por Pedido ($)
ltv_by_cohort['AOV'] = ltv_by_cohort['TotalRevenue'] / ltv_by_cohort['TotalOrders']

# Frecuencia Total Promedio de compras por cliente
ltv_by_cohort['PurchaseFrequency_Total'] = ltv_by_cohort['TotalOrders'] / ltv_by_cohort['TotalCustomers']

# Frecuencia Mensual Promedio de compra
ltv_by_cohort['Monthly_Frequency'] = ltv_by_cohort['PurchaseFrequency_Total'] / ltv_by_cohort['AvgLifespanMonths']

# LTV Real por Cliente ($) = ARPU Histórico por cliente (Ingreso Total / Clientes Totales)
ltv_by_cohort['LTV_Real_Customer'] = ltv_by_cohort['TotalRevenue'] / ltv_by_cohort['TotalCustomers']

# LTV Estimado por Fórmula (AOV * Frecuencia Mensual * Vida Útil)
ltv_by_cohort['LTV_Formula'] = (
    ltv_by_cohort['AOV'] * 
    ltv_by_cohort['Monthly_Frequency'] * 
    ltv_by_cohort['AvgLifespanMonths']
)

# Formatear fecha para impresión
ltv_by_cohort['CohortMonth'] = ltv_by_cohort['CohortMonth'].dt.strftime('%Y-%m')

print("\n--- RESUMEN DE METRICAS DE LTV POR COHORTE ---")
print(ltv_by_cohort[['CohortMonth', 'TotalCustomers', 'AOV', 'Monthly_Frequency', 'AvgLifespanMonths', 'LTV_Real_Customer']].round(2))

# ==========================================
# GENERACIÓN DE GRÁFICA: CURVA DE RETENCIÓN
# ==========================================

print(' ========================================== ')
print(' GENERACIÓN DE GRÁFICA (CURVA DE RETENCIÓN) ')
print(' ========================================== ')

plt.figure(figsize=(12, 6))
plt.title('Curvas de Retención por Cohorte - Online Retail', fontsize=14, fontweight='bold')

# Graficar cada cohorte como una línea independiente
for cohort in retention.index:
    plt.plot(
        retention.columns, 
        retention.loc[cohort], 
        marker='o', 
        linewidth=1.5, 
        label=cohort.strftime('%Y-%m')
    )

plt.xlabel('Meses transcurridos desde la 1ª compra (Cohort Index)', fontsize=11)
plt.ylabel('Porcentaje de Retención (%)', fontsize=11)
plt.xticks(retention.columns)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(title='Cohorte', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()

# Guardar la gráfica
plt.savefig('curva_retencion.png', dpi=300)
print("[OK] Gráfica guardada exitosamente como 'curva_retencion.png'")