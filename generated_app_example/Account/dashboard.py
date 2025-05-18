import streamlit as st
from loguru import logger
import pandas as pd
import plotly.graph_objects as go
from generate_app.z_apps.interfaces.dashboard_w import DashboardInterface

# Style CSS pour le tableau
st.markdown("""
<style>
    .stDataFrame {
        width: 100% !important;
    }
    .st-emotion-cache-13xfhd9 {
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)


# Conteneur principal
with st.container():
    logger.debug(f"Dashboard, role: {st.session_state.user.role}, Id: {st.session_state.user.user_id}")
    
    try: 
        dashboard = DashboardInterface()
        create, qualification, resolve, total, my_incidents = dashboard.get_stats()
    except Exception as e:
        st.error(f"Error while getting stats: {e}")
        total, create, qualification, resolve, my_incidents = 0, 0, 0, 0, 0
    
    # Affichage des statistiques principales
    st.subheader("Incidents Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Incidents instruits", create)
    with col2:
        st.metric("Incidents en cour de qualification", qualification)
    with col3:
        st.metric(f"Total de mes incidents (/{total})", my_incidents)
    with col4:
        st.metric(f"Total incident résolut (/{total})", resolve)
st.write("---")
with st.container():
    st.subheader('Dashboard: Open Incidents by type')

    df = dashboard.show_data()

    # Optionnel: renommer les colonnes
    df = df.rename(columns={"ref":"Ref. Incident","username": "Created By", "prd_or_cmp":"Product or lec. parts", "product_family":"Product Family", "probleme_description":"Explain problem", "qrqc_niv1":"QRQC n1"})
    
    if 'index' in df.columns:
        df = df.set_index('index')
    
    if 'color' in df.columns:
        # Conversion des couleurs en pastel
        color_series = '#'+df['color']
        # Fonction qui colorie chaque ligne
        def color_rows(row):
            c = color_series[row.name]
            return [f'background-color: {c}' for _ in row]

        # On retire la colonne "color" pour ne pas l’afficher
        df = df.drop(columns=['color'], errors='ignore')
        df = df.drop(columns=['created_by'], errors='ignore')
        st.dataframe(df.style.apply(color_rows, axis=1), use_container_width=True, hide_index=True)
    else:
        st.dataframe(df, use_container_width=True)
      
def new_func(df,color_series):
    st.subheader("Incidents by Type")
    counts = df["type"].value_counts()
    valid_colors = {
        'International non-conformance': '#424c55',
        'Safety alert': '#356335',
        'Supplier non-conformance': '#4d354c',
        'Custummer Incident': '#633535',
        'Project incident': '#645335'
    }
    # Create a figure with Plotly
    
    
    # Get colors for each type from valid_colors
    type_colors = [valid_colors.get(incident_type, '#000000') for incident_type in counts.index]
    
    fig = go.Figure(data=[
        go.Bar(
            x=counts.index,
            y=counts.values,
            marker_color=list(type_colors)
        )
    ])
    
    # Update layout for better appearance
    fig.update_layout(
        xaxis_title="Type",
        yaxis_title="Count",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.write("---")
with st.container():
    # Graphique simple
    col1, col2,col3 = st.columns(3)
    with col1:
        new_func(df,color_series)
    with col2:
        st.subheader("Incidents by Severity")
        counts = df["severity"].value_counts()
        
        severity_colors = {
            'Problème sécurité': '#ee9c7f',
            'Perte de fonction principale ou incident client majeur': '#ca9603', 
            'Réduction significative de performance ou de confort': '#771469',
            'Low': '#C2C2C2'
        }
        
        # Get colors for each severity level
        severity_type_colors = [severity_colors.get(severity, '#000000') for severity in counts.index]
        
        fig = go.Figure(data=[
            go.Bar(
            x=counts.index,
            y=counts.values,
            marker_color=severity_type_colors
            )
        ])
        
        fig.update_layout(
            xaxis_title="Severity",
            yaxis_title="Count",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        # Incidents par priorité M1 et M2
        st.subheader("Incidents by Priority (M1/M2)")
        
        # Create separate distributions for M1 and M2
        m1_counts = df["priority_m1"].value_counts()
        m2_counts = df["priority_m2"].value_counts()
        
        # Create Plotly figure
        fig = go.Figure()
        
        # Add M1 distribution
        fig.add_trace(go.Bar(
            name='M1 Priority',
            x=m1_counts.index,
            y=m1_counts.values,
            marker_color='#356335',
            width=0.8,  # Increased width to make bars touch
            offset=-0.4  # Offset to left
        ))
        
        # Add M2 distribution
        fig.add_trace(go.Bar(
            name='M2 Priority',
            x=m2_counts.index,
            y=m2_counts.values,
            marker_color='#633535',
            width=0.8,  # Increased width to make bars touch
            offset=0.4  # Offset to right
        ))

        fig.update_layout(
            barmode='overlay',  # Changed to overlay mode
            xaxis_title="Priority Level",
            yaxis_title="Count",
            showlegend=True,
            legend_title_text="Priority Type",
            bargap=0.8  # Add gap between M1 and M2 groups
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show priority distributions in tables
        col1, col2 = st.columns(2)
        with col1:
            st.write("M1 Priority Distribution:")
            st.dataframe(m1_counts)
        with col2:
            st.write("M2 Priority Distribution:")
            st.dataframe(m2_counts)
            
st.write("---")
# graphique en camber répartitio par site. Si pas de site ajouter les sans site 