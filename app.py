import streamlit as st
import numpy as np
import pandas as pd
from data.fetcher import data_fetcher
from core.portfolio import portfolio
from core.analyser import analyser
from core.optimiser import optimiser

# ── page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio Analyser",
    page_icon="📈",
    layout="wide"
)

# ── session state init ────────────────────────────────────────
if 'screen' not in st.session_state:
    st.session_state.screen = 'landing'
if 'tickers' not in st.session_state:
    st.session_state.tickers = []
if 'weights' not in st.session_state:
    st.session_state.weights = []
if 'portfolio_obj' not in st.session_state:
    st.session_state.portfolio_obj = None
if 'analyser_obj' not in st.session_state:
    st.session_state.analyser_obj = None
if 'optimiser_obj' not in st.session_state:
    st.session_state.optimiser_obj = None


# ── screen 1: landing ─────────────────────────────────────────
def render_landing():
    st.title("📈 Portfolio Analyser")
    st.subheader("Institutional-grade portfolio analysis for every investor.")
    
    st.write("""
    Most investors don't know if their portfolio is actually efficient.
    This tool tells you exactly where you stand — and how to improve.
    """)

    st.markdown("### How it works")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**1. Input your portfolio**")
        st.write("Enter your tickers and how much you hold in each.")
    with col2:
        st.markdown("**2. We run the analysis**")
        st.write("We fetch real market data and apply Modern Portfolio Theory.")
    with col3:
        st.markdown("**3. Get your results**")
        st.write("See your risk, return, Sharpe ratio, and how to optimise.")

    st.divider()
    if st.button("Get Started →", type="primary"):
        st.session_state.screen = 'input'
        st.rerun()


# ── screen 2: input ───────────────────────────────────────────
def render_input():
    st.title("Your Portfolio")
    st.write("Enter each ticker and its weight as a percentage. Weights must sum to 100%.")

    # dynamic rows using session state
    if 'rows' not in st.session_state:
        st.session_state.rows = [{"ticker": "", "weight": 0.0}]

    for i, row in enumerate(st.session_state.rows):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.session_state.rows[i]["ticker"] = st.text_input(
                f"Ticker {i+1}", value=row["ticker"], key=f"ticker_{i}"
            ).upper()
        with col2:
            st.session_state.rows[i]["weight"] = st.number_input(
                f"Weight % {i+1}", min_value=0.0, max_value=100.0,
                value=row["weight"], key=f"weight_{i}"
            )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("+ Add Asset"):
            st.session_state.rows.append({"ticker": "", "weight": 0.0})
            st.rerun()

    total_weight = sum(r["weight"] for r in st.session_state.rows)
    st.write(f"**Total weight: {total_weight:.1f}%**")
    if total_weight != 100.0:
        st.warning("Weights must sum to 100%")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.screen = 'landing'
            st.rerun()
    with col2:
        if st.button("Next →", type="primary", disabled=total_weight != 100.0):
            st.session_state.tickers = [r["ticker"] for r in st.session_state.rows]
            st.session_state.weights = [r["weight"] / 100 for r in st.session_state.rows]
            st.session_state.screen = 'preferences'
            st.rerun()


# ── screen 3: preferences ─────────────────────────────────────
def render_preferences():
    st.title("Preferences")
    st.write("Configure your analysis settings.")

    years = st.slider("Historical data period (years)", 1, 10, 5)
    rf = st.number_input("Risk-free rate (%)", min_value=0.0, max_value=10.0, value=5.0) / 100

    st.session_state.years = years
    st.session_state.rf = rf

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.screen = 'input'
            st.rerun()
    with col2:
        if st.button("Run Analysis →", type="primary"):
            st.session_state.screen = 'loading'
            st.rerun()


# ── screen 4: loading ─────────────────────────────────────────
def render_loading():
    st.title("Running Analysis...")

    with st.spinner("Fetching price data..."):
        fetcher = data_fetcher(st.session_state.tickers, st.session_state.years)
        prices_df = fetcher.fetch_daily()
        spy_df = fetcher.fetch_spy()

    with st.spinner("Building portfolio..."):
        p = portfolio(st.session_state.tickers, st.session_state.weights, prices_df)

    with st.spinner("Running analysis..."):
        a = analyser(spy_df, p.returns_df, p.covariance_matrix, p.weights, p.portfolio_volatility)

    with st.spinner("Running Monte Carlo optimisation (10,000 simulations)..."):
        o = optimiser(p.weights, p.expected_returns_df, p.covariance_matrix)

    # store everything in session state
    st.session_state.portfolio_obj = p
    st.session_state.analyser_obj = a
    st.session_state.optimiser_obj = o

    st.session_state.screen = 'analysis'
    st.rerun()


# ── screen 5: analysis ────────────────────────────────────────
def render_analysis():
    p = st.session_state.portfolio_obj
    a = st.session_state.analyser_obj
    o = st.session_state.optimiser_obj

    st.title("Portfolio Analysis")

    # ── section 1: summary cards ──
    st.header("Portfolio Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Expected Annual Return", f"{p.portfolio_expected_return:.1%}")
    with col2:
        st.metric("Annual Volatility", f"{p.portfolio_volatility:.1%}")
    with col3:
        st.metric("Sharpe Ratio", f"{p.sharpe_ratio:.2f}")
    with col4:
        st.metric("Max Drawdown", f"{a.max_drawdown.mean():.1%}")

    st.divider()

    # ── section 2: efficient frontier ──
    st.header("Efficient Frontier")
    render_frontier(p, o)

    st.divider()

    # ── section 3: correlation heatmap ──
    st.header("Correlation Matrix")
    render_heatmap(p)

    st.divider()

    # ── section 4: asset breakdown ──
    st.header("Individual Asset Breakdown")
    render_asset_table(p, a)

    st.divider()

    # ── section 5: optimiser ──
    st.header("Portfolio Optimiser")
    render_optimiser(p, o)

    if st.button("← Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ── charts ────────────────────────────────────────────────────
def render_frontier(p, o):
    import plotly.graph_objects as go

    mc = o.monte_carlo_df
    max_sharpe_row = mc.loc[o.max_sharpe]
    min_var_row = mc.loc[o.get_min_variance()]

    fig = go.Figure()

    # all monte carlo portfolios
    fig.add_trace(go.Scatter(
        x=mc['volatility'], y=mc['expected_return'],
        mode='markers',
        marker=dict(color=mc['sharpe_ratio'], colorscale='Viridis', size=3, opacity=0.5),
        name='Possible Portfolios'
    ))

    # current portfolio
    fig.add_trace(go.Scatter(
        x=[p.portfolio_volatility], y=[p.portfolio_expected_return],
        mode='markers', marker=dict(color='red', size=15, symbol='star'),
        name='Your Portfolio'
    ))

    # max sharpe
    fig.add_trace(go.Scatter(
        x=[max_sharpe_row['volatility']], y=[max_sharpe_row['expected_return']],
        mode='markers', marker=dict(color='gold', size=15, symbol='star'),
        name='Max Sharpe'
    ))

    # min variance
    fig.add_trace(go.Scatter(
        x=[min_var_row['volatility']], y=[min_var_row['expected_return']],
        mode='markers', marker=dict(color='green', size=15, symbol='star'),
        name='Min Variance'
    ))

    fig.update_layout(
        xaxis_title='Volatility (Risk)',
        yaxis_title='Expected Return',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)


def render_heatmap(p):
    import plotly.graph_objects as go

    corr = p.correlation_matrix
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale='RdBu',
        zmid=0,
        text=corr.round(2).values,
        texttemplate='%{text}'
    ))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def render_asset_table(p, a):
    df = pd.DataFrame({
        'Ticker': p.tickers,
        'Weight': [f"{w:.1%}" for w in p.weights],
        'Expected Return': [f"{r:.1%}" for r in p.expected_returns_df],
        'Beta': [f"{b:.2f}" for b in a.beta_per_asset[p.tickers]],
        'Risk Contribution': [f"{r:.1%}" for r in a.RC_percent]
    })
    st.dataframe(df, use_container_width=True)


def render_optimiser(p, o):
    st.write("Move the slider to explore different risk levels and see the optimal weights.")

    target_vol = st.slider(
        "Target Volatility (Risk Level)",
        min_value=float(o.monte_carlo_df['volatility'].min()),
        max_value=float(o.monte_carlo_df['volatility'].max()),
        value=float(p.portfolio_volatility),
        step=0.01
    )

    best = o.optimise_for_risk(target_vol)

    if best is not None and not isinstance(best, type(None)):
        import plotly.graph_objects as go

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Optimised Return", f"{best['expected_return']:.1%}",
                      delta=f"{best['expected_return'] - p.portfolio_expected_return:.1%}")
        with col2:
            st.metric("Optimised Volatility", f"{best['volatility']:.1%}",
                      delta=f"{best['volatility'] - p.portfolio_volatility:.1%}")
        with col3:
            st.metric("Optimised Sharpe", f"{best['sharpe_ratio']:.2f}",
                      delta=f"{best['sharpe_ratio'] - p.sharpe_ratio:.2f}")

        # weights comparison chart
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Current', x=p.tickers, y=p.weights))
        fig.add_trace(go.Bar(name='Optimised', x=p.tickers, y=best['weights']))
        fig.update_layout(barmode='group', xaxis_title='Asset', yaxis_title='Weight', height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No portfolio found near this risk level. Try adjusting the slider.")


# ── router ────────────────────────────────────────────────────
if st.session_state.screen == 'landing':
    render_landing()
elif st.session_state.screen == 'input':
    render_input()
elif st.session_state.screen == 'preferences':
    render_preferences()
elif st.session_state.screen == 'loading':
    render_loading()
elif st.session_state.screen == 'analysis':
    render_analysis()