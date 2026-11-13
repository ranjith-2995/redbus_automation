import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time, json, random, subprocess
from datetime import datetime, timedelta
from pathlib import Path

from ai_assistant.intent_parser import RedBusIntentParser
from ai_assistant.smart_recommender import SmartBusRecommender
from ai_assistant.price_analytics import BusPriceAnalytics
from ai_assistant.conversational_agent import RedBusConversationalAgent
from ai_assistant.bus_comparator import BusComparator
from utils.pdf_ticket_generator import generate_pdf_ticket
from config.config import BASE_DIR, PASSENGER_DATA

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RedBus Pro · AI Booking Platform",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# ADVANCED CSS — GLASSMORPHISM + GRADIENT DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

/* ══ BASE RESET ══ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: #0d0f1a !important;
    color: #e8eaf0 !important;
}
.stApp { background: #0d0f1a !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
.stDeployButton { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }

/* ══ ANIMATED BACKGROUND ══ */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: -1;
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(220,38,38,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 90%, rgba(239,68,68,0.08) 0%, transparent 50%),
        radial-gradient(ellipse 50% 50% at 50% 50%, rgba(30,32,50,0.9) 0%, transparent 100%),
        #0d0f1a;
}

/* ══ RESPONSIVE TOP NAVBAR ══ */
.top-navbar-wrapper {
    background: rgba(13,15,26,0.92);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-bottom: 1px solid rgba(220,38,38,0.22);
    padding: 12px 36px 8px;
    position: sticky; top: 0; z-index: 1000;
    box-shadow: 0 4px 28px rgba(0,0,0,0.55);
}
.brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 26px; font-weight: 800;
    background: linear-gradient(135deg, #fff 30%, #ef4444 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
    white-space: nowrap;
}
.brand em {
    font-style: normal;
    background: linear-gradient(135deg, #ef4444, #fbbf24);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* ══ RESPONSIVE PILLS NAVBAR BUTTONS ══ */
div[data-testid="stPills"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 8px !important;
    flex-wrap: wrap !important;
    margin: 0 !important;
}
div[data-testid="stPills"] button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    color: rgba(255,255,255,0.7) !important;
    border-radius: 50px !important;
    padding: 7px 18px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: none !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    margin: 2px 0 !important;
}
div[data-testid="stPills"] button:hover {
    background: rgba(220,38,38,0.18) !important;
    border-color: rgba(220,38,38,0.4) !important;
    color: #fff !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stPills"] button[aria-checked="true"],
div[data-testid="stPills"] button[aria-pressed="true"],
div[data-testid="stPills"] button[data-state="checked"] {
    background: linear-gradient(135deg, #ef4444, #991b1b) !important;
    border: 1px solid rgba(239,68,68,0.5) !important;
    color: #fff !important;
    box-shadow: 0 4px 16px rgba(220,38,38,0.4) !important;
    font-weight: 700 !important;
}

.live-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.4);
    color: #10b981; font-size: 11px; font-weight: 700;
    padding: 5px 12px; border-radius: 20px; letter-spacing: 0.5px;
    white-space: nowrap;
}
.live-dot { width:7px; height:7px; background:#10b981; border-radius:50%;
    animation: blink 1.4s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ══ HERO ══ */
.hero {
    padding: 80px 60px 60px;
    position: relative; overflow: hidden;
    min-height: 500px;
}
.hero-bg-text {
    position: absolute; right: -20px; top: 20px;
    font-size: 280px; font-weight: 900; line-height: 1;
    color: rgba(220,38,38,0.04); pointer-events: none;
    font-family: 'Space Grotesk', sans-serif; letter-spacing: -10px;
    user-select: none;
}
.hero-tag {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(220,38,38,0.1); border: 1px solid rgba(220,38,38,0.3);
    color: #f87171; padding: 6px 16px; border-radius: 50px;
    font-size: 12px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; margin-bottom: 24px;
}
.hero-h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 68px; font-weight: 800; line-height: 1.0;
    color: #fff; margin-bottom: 20px; letter-spacing: -2px;
}
.hero-h1 .grad {
    background: linear-gradient(135deg, #ef4444 0%, #fbbf24 50%, #ef4444 100%);
    background-size: 200% 200%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: gradMove 4s ease infinite;
}
@keyframes gradMove { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
.hero-sub {
    font-size: 18px; color: rgba(255,255,255,0.5);
    max-width: 540px; line-height: 1.6; margin-bottom: 40px;
    font-weight: 400;
}

/* ══ STAT BADGES ══ */
.stats-row { display: flex; gap: 32px; margin-bottom: 48px; }
.stat-badge {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 16px 24px;
    text-align: center; min-width: 110px;
    backdrop-filter: blur(10px);
    transition: all 0.3s;
}
.stat-badge:hover {
    border-color: rgba(220,38,38,0.4);
    background: rgba(220,38,38,0.08);
    transform: translateY(-3px);
}
.stat-n { font-family:'Space Grotesk',sans-serif; font-size:26px; font-weight:800; color:#ef4444; }
.stat-l { font-size:11px; color:rgba(255,255,255,0.4); text-transform:uppercase; letter-spacing:1px; margin-top:3px; }

/* ══ GLASS SEARCH CARD ══ */
.glass-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 32px 36px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.08);
}
.glass-card-title {
    font-size: 11px; font-weight: 700; color: #ef4444;
    text-transform: uppercase; letter-spacing: 2px; margin-bottom: 20px;
    display: flex; align-items: center; gap: 8px;
}
.glass-card-title::before { content:''; width:20px; height:2px; background:#ef4444; border-radius:1px; }

/* ══ ROUTE CHIPS ══ */
.chip-row { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px; }
.chip {
    background: rgba(220,38,38,0.08); border: 1px solid rgba(220,38,38,0.25);
    color: #f87171; font-size:12px; font-weight:600;
    padding:6px 14px; border-radius:50px; cursor:pointer; transition:all 0.2s;
}
.chip:hover { background:rgba(220,38,38,0.2); border-color:#ef4444; color:#fff; }

/* ══ BUS CARD — ADVANCED ══ */
.bus-card-adv {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 24px 28px;
    margin-bottom: 16px; position: relative; overflow: hidden;
    transition: all 0.35s ease;
    cursor: pointer;
}
.bus-card-adv::before {
    content: '';
    position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
    background: linear-gradient(180deg, #ef4444, #fbbf24);
    border-radius: 4px 0 0 4px;
}
.bus-card-adv:hover {
    background: rgba(220,38,38,0.07);
    border-color: rgba(220,38,38,0.35);
    transform: translateX(4px);
    box-shadow: 0 8px 40px rgba(220,38,38,0.15), -4px 0 0 #ef4444;
}
.bus-card-adv.featured::before { background: linear-gradient(180deg,#fbbf24,#ef4444); }
.bus-card-adv.economy::before { background: linear-gradient(180deg,#10b981,#059669); }

.bca-top { display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:16px; }
.bca-name { font-family:'Space Grotesk',sans-serif; font-size:18px; font-weight:700; color:#fff; }
.bca-type {
    font-size:11px; font-weight:700; padding:4px 12px; border-radius:50px;
    text-transform:uppercase; letter-spacing:0.5px; display:inline-block; margin-top:5px;
}
.bca-type.ac { background:rgba(59,130,246,0.15); color:#60a5fa; border:1px solid rgba(59,130,246,0.3); }
.bca-type.sleeper { background:rgba(251,191,36,0.1); color:#fbbf24; border:1px solid rgba(251,191,36,0.3); }
.bca-type.eco { background:rgba(16,185,129,0.1); color:#10b981; border:1px solid rgba(16,185,129,0.3); }

.bca-fare { text-align:right; }
.bca-price { font-family:'Space Grotesk',sans-serif; font-size:28px; font-weight:800; color:#fff; }
.bca-price-sub { font-size:12px; color:rgba(255,255,255,0.35); }
.bca-oldp { font-size:13px; color:rgba(255,255,255,0.3); text-decoration:line-through; }
.bca-save { font-size:11px; color:#10b981; font-weight:700; margin-top:2px; }

.bca-route { display:flex; align-items:center; gap:20px; margin:16px 0; }
.bca-time { font-family:'Space Grotesk',sans-serif; font-size:22px; font-weight:700; color:#fff; }
.bca-city { font-size:11px; color:rgba(255,255,255,0.4); margin-top:2px; letter-spacing:0.5px; }
.bca-line { flex:1; display:flex; flex-direction:column; align-items:center; gap:4px; }
.bca-dots { display:flex; align-items:center; gap:0; width:100%; }
.bca-dot { width:8px; height:8px; border-radius:50%; background:#ef4444; flex-shrink:0; }
.bca-seg { flex:1; height:2px; background:linear-gradient(90deg, #ef4444, rgba(251,191,36,0.6), #ef4444); }
.bca-dur { font-size:11px; color:rgba(255,255,255,0.4); font-weight:600; letter-spacing:0.5px; }

.bca-bottom { display:flex; align-items:center; justify-content:space-between; }
.bca-amenities { display:flex; gap:6px; flex-wrap:wrap; }
.bca-chip {
    font-size:10px; padding:3px 10px; border-radius:50px; font-weight:600;
    background:rgba(255,255,255,0.05); color:rgba(255,255,255,0.5);
    border:1px solid rgba(255,255,255,0.08);
}
.bca-seats { text-align:center; }
.bca-seats-n { font-family:'Space Grotesk',sans-serif; font-size:20px; font-weight:800; }
.bca-seats-l { font-size:10px; color:rgba(255,255,255,0.4); text-transform:uppercase; letter-spacing:1px; }
.bca-rating { display:flex; align-items:center; gap:5px; font-size:13px; font-weight:700; color:#fbbf24; }

/* ══ SEAT MAP ══ */
.seat-wrapper {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 28px; margin-bottom: 20px;
}
.deck-title {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 2px; color: rgba(255,255,255,0.4); margin-bottom: 20px;
    display: flex; align-items: center; gap: 10px;
}
.deck-title::after { content:''; flex:1; height:1px; background:rgba(255,255,255,0.08); }
.bus-nose {
    background: linear-gradient(135deg, #ef4444, #991b1b);
    border-radius: 12px; height: 48px;
    display: flex; align-items: center; justify-content: center;
    color: rgba(255,255,255,0.9); font-weight: 800; font-size: 12px;
    letter-spacing: 3px; text-transform: uppercase;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(220,38,38,0.4);
}
.seat-legend { display:flex; gap:20px; justify-content:center; margin-bottom:20px; flex-wrap:wrap; }
.sleg { display:flex; align-items:center; gap:7px; font-size:11px; color:rgba(255,255,255,0.5); font-weight:500; }
.sleg-sq { width:14px; height:14px; border-radius:4px; }

/* ══ BOOKING PANEL ══ */
.booking-glass {
    background: rgba(220,38,38,0.05);
    border: 1px solid rgba(220,38,38,0.2);
    border-radius: 20px; padding: 28px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.bp-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 14px; font-weight: 700; color: #ef4444;
    text-transform: uppercase; letter-spacing: 2px; margin-bottom: 20px;
}
.bp-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
}
.bp-row:last-of-type { border-bottom: none; }
.bp-k { font-size: 12px; color: rgba(255,255,255,0.4); font-weight: 500; }
.bp-v { font-size: 13px; color: #fff; font-weight: 700; }
.bp-total {
    margin-top: 20px;
    background: linear-gradient(135deg, #ef4444, #991b1b);
    border-radius: 14px; padding: 18px 24px; text-align: center;
    box-shadow: 0 8px 24px rgba(220,38,38,0.4);
}
.bp-total-l { font-size: 10px; color: rgba(255,255,255,0.7); letter-spacing: 2px; text-transform:uppercase; }
.bp-total-v { font-family:'Space Grotesk',sans-serif; font-size:34px; font-weight:800; color:#fbbf24; line-height:1.1; }
.bp-total-t { font-size:11px; color:rgba(255,255,255,0.5); margin-top:4px; }

/* ══ TICKET ══ */
.ticket {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(220,38,38,0.25);
    border-radius: 24px; overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.ticket-head {
    background: linear-gradient(135deg, #ef4444 0%, #991b1b 60%, #1a0a0a 100%);
    padding: 28px 32px;
    display: flex; justify-content: space-between; align-items: center;
    position: relative; overflow: hidden;
}
.ticket-head::after {
    content: '🚌';
    position: absolute; right: 24px; bottom: -10px;
    font-size: 90px; opacity: 0.12;
}
.th-brand { font-family:'Space Grotesk',sans-serif; font-size:22px; font-weight:800; color:#fff; }
.th-pnr-l { font-size:10px; color:rgba(255,255,255,0.5); letter-spacing:2px; text-transform:uppercase; }
.th-pnr-v { font-family:'Space Grotesk',sans-serif; font-size:20px; font-weight:800; color:#fbbf24; }
.ticket-body { padding: 32px; }
.tc-route { display:flex; align-items:center; gap:20px; margin-bottom:28px; }
.tc-city { font-family:'Space Grotesk',sans-serif; font-size:32px; font-weight:800; color:#fff; }
.tc-mid { flex:1; text-align:center; }
.tc-arr { font-size:28px; }
.tc-dur { font-size:11px; color:rgba(255,255,255,0.4); margin-top:4px; letter-spacing:1px; }
.tc-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }
.tc-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 16px; text-align: center;
}
.tc-bl { font-size:10px; color:rgba(255,255,255,0.4); text-transform:uppercase; letter-spacing:1px; }
.tc-bv { font-size:15px; font-weight:700; color:#fff; margin-top:5px; }
.tc-status {
    background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3);
    border-radius: 14px; padding: 14px 20px;
    display: flex; align-items: center; gap: 12px; margin-top: 20px;
}
.tc-sdot { width:10px; height:10px; background:#10b981; border-radius:50%; animation:blink 1.4s infinite; }
.tc-stxt { font-size:14px; font-weight:700; color:#10b981; }
.tc-perforations {
    border-top: 2px dashed rgba(255,255,255,0.08);
    margin: 0 32px 24px;
    position: relative;
}
.tc-perforations::before, .tc-perforations::after {
    content: '';
    position: absolute; top: -12px;
    width: 24px; height: 24px; background: #0d0f1a;
    border-radius: 50%;
}
.tc-perforations::before { left: -44px; }
.tc-perforations::after { right: -44px; }

/* ══ DASHBOARD ══ */
.kpi-row { display:grid; grid-template-columns:repeat(4,1fr); gap:20px; }
.kpi-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 24px;
    position: relative; overflow: hidden;
    transition: all 0.3s;
}
.kpi-card:hover {
    border-color: rgba(220,38,38,0.3);
    background: rgba(220,38,38,0.05);
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}
.kpi-card::after {
    content: '';
    position: absolute; top: 0; right: 0;
    width: 80px; height: 80px;
    border-radius: 0 20px 0 80px;
    opacity: 0.06;
}
.kpi-card.red::after { background: #ef4444; }
.kpi-card.green::after { background: #10b981; }
.kpi-card.blue::after { background: #3b82f6; }
.kpi-card.amber::after { background: #fbbf24; }
.kpi-icon { font-size: 32px; margin-bottom: 14px; }
.kpi-num { font-family:'Space Grotesk',sans-serif; font-size:34px; font-weight:800; color:#fff; line-height:1; }
.kpi-label { font-size:12px; color:rgba(255,255,255,0.4); margin-top:6px; font-weight:500; }
.kpi-trend { font-size:12px; font-weight:700; margin-top:10px; display:flex; align-items:center; gap:4px; }
.kpi-trend.up { color:#10b981; }
.kpi-trend.dn { color:#ef4444; }

/* ══ AI CHAT ══ */
.chat-wrap {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; overflow: hidden;
}
.chat-hdr {
    background: linear-gradient(135deg, rgba(220,38,38,0.2), rgba(153,27,27,0.3));
    border-bottom: 1px solid rgba(220,38,38,0.2);
    padding: 18px 24px; display:flex; align-items:center; gap:14px;
}
.chat-av {
    width:42px; height:42px; border-radius:50%;
    background: linear-gradient(135deg, #ef4444, #fbbf24);
    display:flex; align-items:center; justify-content:center;
    font-size:20px; flex-shrink:0;
    box-shadow: 0 4px 16px rgba(220,38,38,0.4);
}
.chat-name { font-weight:700; color:#fff; font-size:15px; }
.chat-status { font-size:11px; color:#10b981; display:flex; align-items:center; gap:5px; margin-top:2px; }
.chat-msgs {
    padding: 20px; min-height: 350px; max-height: 420px;
    overflow-y: auto; background: rgba(0,0,0,0.2);
}
.msg { display:flex; margin-bottom:16px; }
.msg.bot { justify-content:flex-start; }
.msg.user { justify-content:flex-end; }
.bubble {
    max-width:72%; padding:14px 18px;
    font-size:14px; line-height:1.6; border-radius:18px;
}
.bubble.bot {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    color: #e8eaf0; border-radius: 4px 18px 18px 18px;
}
.bubble.user {
    background: linear-gradient(135deg, #ef4444, #991b1b);
    color: #fff; border-radius: 18px 4px 18px 18px;
    box-shadow: 0 4px 16px rgba(220,38,38,0.3);
}

/* ══ TEST LAB ══ */
.test-suite-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px; padding: 22px 26px;
    margin-bottom: 14px; display:flex; align-items:center; gap:20px;
    transition: all 0.3s;
}
.test-suite-card:hover {
    border-color: rgba(220,38,38,0.3);
    background: rgba(220,38,38,0.04);
}
.ts-icon { font-size:34px; flex-shrink:0; }
.ts-info { flex:1; }
.ts-name { font-weight:700; font-size:15px; color:#fff; margin-bottom:4px; }
.ts-desc { font-size:12px; color:rgba(255,255,255,0.4); }
.ts-path { font-size:11px; color:rgba(255,255,255,0.25); font-family:monospace; margin-top:4px; }
.ts-badge {
    padding:5px 14px; border-radius:50px;
    font-size:11px; font-weight:800; letter-spacing:0.5px;
}
.ts-badge.pass { background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3); }
.ts-badge.fail { background:rgba(220,38,38,0.15); color:#ef4444; border:1px solid rgba(220,38,38,0.3); }
.ts-badge.run  { background:rgba(59,130,246,0.15); color:#60a5fa; border:1px solid rgba(59,130,246,0.3); }
.ts-badge.idle { background:rgba(255,255,255,0.05); color:rgba(255,255,255,0.4); border:1px solid rgba(255,255,255,0.1); }
.terminal {
    background: #060810; border-radius: 14px; padding: 20px;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 12px; line-height: 1.6; color: #4ade80;
    border: 1px solid rgba(74,222,128,0.2);
    max-height: 320px; overflow-y: auto;
    margin: 0 0 16px; white-space: pre-wrap;
}
.terminal .err { color: #f87171; }
.terminal .warn { color: #fbbf24; }
.terminal .info { color: #60a5fa; }

/* ══ SECTION WRAPPER ══ */
.sec { padding: 40px 48px; }
.sec-hdr { display:flex; align-items:center; justify-content:space-between; margin-bottom:28px; }
.sec-title { font-family:'Space Grotesk',sans-serif; font-size:24px; font-weight:800; color:#fff; }
.sec-title span { color:#ef4444; }
.sec-sub { font-size:13px; color:rgba(255,255,255,0.4); margin-top:4px; }
.sec-pill {
    background: rgba(220,38,38,0.1); border: 1px solid rgba(220,38,38,0.3);
    color: #f87171; font-size:12px; font-weight:700;
    padding: 6px 16px; border-radius:50px; letter-spacing:0.5px;
}

/* ══ HIDE DEFAULT TABS (REPLACED BY RESPONSIVE PILLS NAVBAR) ══ */
div[data-testid="stTabs"] > div:first-child,
.stTabs [data-baseweb="tab-list"],
.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    visibility: hidden !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 0 !important;
}

/* ══ STREAMLIT COMPONENTS OVERRIDES ══ */
.stButton > button {
    background: linear-gradient(135deg, #ef4444, #991b1b) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important; padding: 12px 28px !important;
    font-weight: 700 !important; font-size: 13px !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 4px 20px rgba(220,38,38,0.35) !important;
    transition: all 0.25s !important; width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(220,38,38,0.5) !important;
}
.stButton > button:disabled {
    background: rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.3) !important;
    box-shadow: none !important; transform: none !important;
}
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stTextInput"] input,
div[data-testid="stDateInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important; color: #fff !important;
    font-size: 14px !important;
}
div[data-testid="stSelectbox"] > div > div:focus-within,
div[data-testid="stTextInput"] input:focus,
div[data-testid="stDateInput"] input:focus {
    border-color: #ef4444 !important;
    box-shadow: 0 0 0 3px rgba(220,38,38,0.15) !important;
}
.stSelectbox label, .stTextInput label, .stDateInput label,
.stRadio label, .stSlider label, .stMultiSelect label {
    color: rgba(255,255,255,0.6) !important;
    font-size: 12px !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 1px !important;
}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important; padding: 16px 20px !important;
}
.stMetricValue { color: #fff !important; }
.stMetricLabel { color: rgba(255,255,255,0.5) !important; }
.stSlider [data-testid="stSlider"] > div { background: rgba(255,255,255,0.1) !important; }
.stAlert { border-radius: 12px !important; }
div[data-testid="stMultiSelect"] > div { background:rgba(255,255,255,0.05) !important; border-color:rgba(255,255,255,0.1) !important; }
.stDownloadButton > button {
    background: rgba(16,185,129,0.15) !important;
    color: #10b981 !important; border: 1px solid rgba(16,185,129,0.3) !important;
    border-radius: 12px !important;
}
div[data-testid="stSuccess"] { background: rgba(16,185,129,0.1) !important; border-color: rgba(16,185,129,0.3) !important; }
div[data-testid="stWarning"] { background: rgba(251,191,36,0.1) !important; border-color: rgba(251,191,36,0.3) !important; }
div[data-testid="stInfo"] { background: rgba(59,130,246,0.1) !important; border-color: rgba(59,130,246,0.3) !important; }

/* ══ SCROLLBAR ══ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); border-radius:3px; }
::-webkit-scrollbar-thumb { background: rgba(220,38,38,0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #ef4444; }

/* ══ RESPONSIVE ADAPTATIONS (MOBILE & TABLET) ══ */
@media screen and (max-width: 1024px) {
    .navbar { padding: 0 20px; }
    .hero { padding: 50px 24px 36px; }
    .hero-h1 { font-size: 44px; }
    .hero-bg-text { font-size: 160px; }
    .sec { padding: 24px 20px; }
    .kpi-row { grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .tc-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
    .stTabs [data-baseweb="tab-list"] { padding: 0 16px !important; }
}

@media screen and (max-width: 768px) {
    .navbar {
        padding: 12px 16px;
        height: auto;
        flex-direction: column;
        gap: 10px;
        align-items: flex-start;
    }
    .brand { font-size: 22px; }
    .nav-pill { padding: 5px 12px; font-size: 12px; }
    .hero {
        padding: 32px 16px 24px;
        min-height: auto;
    }
    .hero-h1 { font-size: 32px; letter-spacing: -1px; }
    .hero-sub { font-size: 14px; margin-bottom: 20px; }
    .hero-bg-text { display: none; }
    .stats-row {
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 24px;
    }
    .stat-badge {
        flex: 1 1 calc(50% - 10px);
        min-width: 90px;
        padding: 12px 14px;
    }
    .stat-n { font-size: 20px; }
    .stat-l { font-size: 10px; }
    .sec { padding: 18px 12px; }
    .glass-card { padding: 18px 14px; border-radius: 16px; }
    .chip-row {
        flex-wrap: nowrap;
        overflow-x: auto;
        padding-bottom: 8px;
        -webkit-overflow-scrolling: touch;
    }
    .chip { flex-shrink: 0; }
    .bca-top { flex-direction: column; align-items: flex-start; gap: 8px; }
    .bca-fare { text-align: left; }
    .bca-route { flex-direction: column; align-items: flex-start; gap: 8px; }
    .bca-line { width: 100%; }
    .bca-bottom { flex-direction: column; align-items: flex-start; gap: 10px; }
    .bca-amenities { width: 100%; flex-wrap: wrap; }
    .bca-seats { text-align: left; }
    .tc-route { flex-direction: column; gap: 8px; }
    .tc-city { font-size: 24px; }
    .tc-grid { grid-template-columns: 1fr; gap: 10px; }
    .kpi-row { grid-template-columns: 1fr; gap: 12px; }
    .test-suite-card { flex-direction: column; align-items: flex-start; gap: 12px; }
    .ts-badge { align-self: flex-start; }
    .stTabs [data-baseweb="tab-list"] {
        padding: 0 8px !important;
        overflow-x: auto !important;
        white-space: nowrap !important;
        -webkit-overflow-scrolling: touch !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 12px !important;
        font-size: 12px !important;
    }
    .booking-glass { padding: 16px 14px; }
    .seat-wrapper { padding: 16px 10px; }
    .seat-legend { gap: 8px; }
}

@media screen and (max-width: 480px) {
    .hero-h1 { font-size: 26px; }
    .stat-badge { flex: 1 1 100%; }
    .bca-name { font-size: 15px; }
    .bca-price { font-size: 22px; }
    .bp-total-v { font-size: 26px; }
    .tc-city { font-size: 20px; }
}

.sp { height: 24px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_D = dict(
    src="Chennai", dst="Bangalore",
    travel_date=datetime.today() + timedelta(days=1),
    selected_bus=None, selected_seats=[],
    confirmed_pnr=None,
    passenger_name=PASSENGER_DATA.get("name","Ranjith Kumar"),
    passenger_mobile=PASSENGER_DATA.get("phone","9876543210"),
    passenger_email=PASSENGER_DATA.get("email","user@redbus.in"),
    chat_history=[], agent=None, test_results={},
    active_nav="🏠 Home",
)
for k, v in _D.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────
CITIES = ["Chennai","Bangalore","Mumbai","Delhi","Hyderabad","Pune",
          "Kolkata","Coimbatore","Vizag","Jaipur","Ahmedabad","Nagpur","Bhopal"]

BUSES = [
    {"id":1,"name":"SRS Travels","type":"AC Sleeper","cat":"featured",
     "dep":"21:00","arr":"06:30","dur":"9h 30m","seats":14,
     "fare":950,"old":1200,"rating":4.7,"amenities":["WiFi","Charging","Water","Blanket","Pillow"]},
    {"id":2,"name":"Orange Tours","type":"AC Semi-Sleeper","cat":"default",
     "dep":"22:30","arr":"07:00","dur":"8h 30m","seats":8,
     "fare":750,"old":950,"rating":4.4,"amenities":["Charging","Snacks","Pillow"]},
    {"id":3,"name":"KSRTC Express","type":"Non-AC Seater","cat":"economy",
     "dep":"23:00","arr":"05:30","dur":"6h 30m","seats":31,
     "fare":399,"old":499,"rating":4.0,"amenities":["Charging"]},
    {"id":4,"name":"Greenline Volvo","type":"AC Multi-Axle","cat":"featured",
     "dep":"20:00","arr":"05:30","dur":"9h 30m","seats":5,
     "fare":1299,"old":1599,"rating":4.9,"amenities":["WiFi","USB","Charging","Blanket","Snacks","Entertainment"]},
    {"id":5,"name":"VRL Travels","type":"AC Seater","cat":"default",
     "dep":"07:00","arr":"13:30","dur":"6h 30m","seats":22,
     "fare":599,"old":749,"rating":4.2,"amenities":["Charging","Snacks"]},
]

LOWER = [["L1","L2","","L3","L4"],["L5","L6","","L7","L8"],
         ["L9","L10","","L11","L12"],["L13","L14","","L15","L16"]]
UPPER = [["U1","U2","","U3","U4"],["U5","U6","","U7","U8"],
         ["U9","U10","","U11","U12"],["U13","U14","","U15","U16"]]
BOOKED  = {"L3","L7","L11","U2","U6","U9","U13"}
LADIES  = {"L1","U1"}

# ─────────────────────────────────────────────────────────────────────────────
# RESPONSIVE TOP NAVBAR (PILL BUTTONS)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="top-navbar-wrapper">', unsafe_allow_html=True)
col_nav_brand, col_nav_pills, col_nav_live = st.columns([1.5, 5.8, 0.9], vertical_alignment="center")

with col_nav_brand:
    st.markdown('<div class="brand">red<em>Bus</em> <span style="font-size:11px;font-weight:400;color:rgba(255,255,255,0.3);letter-spacing:2px">PRO</span></div>', unsafe_allow_html=True)

with col_nav_pills:
    active_nav = st.pills(
        label="Navigation Menu",
        options=["🏠 Home", "🚌 Bus Listings", "💺 Seat Selector", "🤖 AI Assistant", "📊 Dashboard", "⚡ Test Lab"],
        default=st.session_state.get("active_nav", "🏠 Home"),
        required=True,
        label_visibility="collapsed",
        key="active_nav"
    )

with col_nav_live:
    st.markdown('<div style="text-align:right"><div class="live-badge"><div class="live-dot"></div> LIVE</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 0 — HOME & SEARCH
# ══════════════════════════════════════════════════════════════════════════════
if active_nav == "🏠 Home":
    # Hero
    st.markdown("""
    <div class="hero">
      <div class="hero-bg-text">BUS</div>
      <div class="hero-tag">🚀 AI-Powered Booking Platform</div>
      <div class="hero-h1">Book Smarter,<br>Travel <span class="grad">Faster.</span></div>
      <div class="hero-sub">India's most advanced bus booking platform — real-time seats, AI recommendations, instant PDF boarding pass.</div>
      <div class="stats-row">
        <div class="stat-badge"><div class="stat-n">2,400+</div><div class="stat-l">Bus Partners</div></div>
        <div class="stat-badge"><div class="stat-n">120K</div><div class="stat-l">Daily Rides</div></div>
        <div class="stat-badge"><div class="stat-n">99.8%</div><div class="stat-l">On-Time</div></div>
        <div class="stat-badge"><div class="stat-n">4.9★</div><div class="stat-l">Rating</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Search glass card
    with st.container():
        st.markdown('<div class="sec" style="padding-top:0;margin-top:-48px">', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="glass-card-title">Search Buses</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="chip-row">
          <span class="chip">Chennai → Bangalore</span>
          <span class="chip">Mumbai → Pune</span>
          <span class="chip">Delhi → Jaipur</span>
          <span class="chip">Hyderabad → Vizag</span>
          <span class="chip">Coimbatore → Chennai</span>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns([2,2,1.5,1])
        with c1:
            st.session_state.src = st.selectbox("🛫 From", CITIES,
                index=CITIES.index(st.session_state.src), key="s_src")
        with c2:
            dlist = [c for c in CITIES if c != st.session_state.src]
            cur = st.session_state.dst if st.session_state.dst in dlist else dlist[0]
            st.session_state.dst = st.selectbox("🛬 To", dlist,
                index=dlist.index(cur), key="s_dst")
        with c3:
            td = st.date_input("📅 Travel Date",
                value=st.session_state.travel_date.date(), key="s_date")
            st.session_state.travel_date = datetime.combine(td, datetime.min.time())
        with c4:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("🔍  Search", key="btn_search"):
                st.session_state.selected_bus = None
                st.session_state.selected_seats = []
                st.session_state["active_nav"] = "🚌 Bus Listings"
                st.rerun()

        st.markdown('</div></div>', unsafe_allow_html=True)

    # Feature cards row
    st.markdown('<div class="sec">', unsafe_allow_html=True)
    fc = st.columns(4)
    for col, ico, ttl, dsc in [
        (fc[0],"🤖","AI Smart Search","ML-powered recommendations based on your travel patterns"),
        (fc[1],"💺","Live Seat Map","Interactive seat picker with real-time availability"),
        (fc[2],"📄","Instant Boarding Pass","Auto PDF with QR code, generated in seconds"),
        (fc[3],"🧪","Automation Suite","Full Selenium + PyTest SDET framework"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card red" style="text-align:center;padding:28px 20px;">
              <div style="font-size:40px;margin-bottom:14px">{ico}</div>
              <div style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;color:#fff;margin-bottom:8px">{ttl}</div>
              <div style="font-size:12px;color:rgba(255,255,255,0.4);line-height:1.6">{dsc}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Confirmed Ticket
    if st.session_state.confirmed_pnr:
        pnr = st.session_state.confirmed_pnr
        bus = st.session_state.selected_bus or BUSES[0]
        seats_s = ", ".join(st.session_state.selected_seats) or "L2"
        cnt = max(len(st.session_state.selected_seats), 1)
        fare = bus["fare"] * cnt
        tax  = int(fare * 0.05)
        total = fare + tax

        st.markdown('<div class="sec" style="padding-top:0">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="ticket">
          <div class="ticket-head">
            <div>
              <div class="th-brand">🚌 redBus PRO</div>
              <div style="font-size:13px;color:rgba(255,255,255,0.6);margin-top:4px">Booking Confirmed</div>
            </div>
            <div style="text-align:right">
              <div class="th-pnr-l">PNR NUMBER</div>
              <div class="th-pnr-v">{pnr}</div>
            </div>
          </div>
          <div class="ticket-body">
            <div class="tc-route">
              <div>
                <div class="tc-city">{st.session_state.src}</div>
                <div style="font-size:11px;color:rgba(255,255,255,0.35);margin-top:3px">{bus['dep']}</div>
              </div>
              <div class="tc-mid">
                <div class="tc-arr">✈️</div>
                <div class="tc-dur">{bus['dur']}</div>
              </div>
              <div style="text-align:right">
                <div class="tc-city">{st.session_state.dst}</div>
                <div style="font-size:11px;color:rgba(255,255,255,0.35);margin-top:3px">{bus['arr']}</div>
              </div>
            </div>
            <div class="tc-grid">
              <div class="tc-box"><div class="tc-bl">Passenger</div><div class="tc-bv">{st.session_state.passenger_name}</div></div>
              <div class="tc-box"><div class="tc-bl">Seat(s)</div><div class="tc-bv" style="color:#fbbf24">{seats_s}</div></div>
              <div class="tc-box"><div class="tc-bl">Bus</div><div class="tc-bv">{bus['name']}</div></div>
              <div class="tc-box"><div class="tc-bl">Total Fare</div><div class="tc-bv" style="color:#ef4444">₹{total:,}</div></div>
            </div>
            <div class="tc-status">
              <div class="tc-sdot"></div>
              <div class="tc-stxt">✅ CONFIRMED — Have a safe journey, {st.session_state.passenger_name}!</div>
            </div>
          </div>
          <div class="tc-perforations"></div>
        </div>
        """, unsafe_allow_html=True)

        try:
            pdf_bytes = generate_pdf_ticket({
                "pnr": pnr,
                "passenger_name": st.session_state.passenger_name,
                "passenger_mobile": st.session_state.passenger_mobile,
                "src": st.session_state.src,
                "dst": st.session_state.dst,
                "source": st.session_state.src,
                "destination": st.session_state.dst,
                "bus_name": bus["name"],
                "seat": seats_s,
                "seat_no": seats_s,
                "fare": total,
                "departure": bus["dep"],
                "arrival": bus["arr"],
                "travel_date": st.session_state.travel_date.strftime("%d %b %Y"),
            })
            st.download_button(
                label="📄  Download Boarding Pass (PDF)",
                data=pdf_bytes,
                file_name=f"ticket_{pnr}.pdf",
                mime="application/pdf",
                key="dl_pdf"
            )
        except Exception as e:
            st.warning(f"PDF error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — BUS LISTINGS
# ══════════════════════════════════════════════════════════════════════════════
elif active_nav == "🚌 Bus Listings":
    st.markdown('<div class="sec">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sec-hdr">
      <div>
        <div class="sec-title">{st.session_state.src} <span>→</span> {st.session_state.dst}</div>
        <div class="sec-sub">{st.session_state.travel_date.strftime("%A, %d %B %Y")} &nbsp;·&nbsp; {len(BUSES)} buses available</div>
      </div>
      <div class="sec-pill">🔴 Live Inventory</div>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    fa, fb, fc2, fd = st.columns(4)
    with fa:
        f_type = st.multiselect("Bus Type",
            ["AC Sleeper","AC Semi-Sleeper","Non-AC Seater","AC Multi-Axle","AC Seater"],
            key="fl_type")
    with fb:
        f_fare = st.slider("Max Fare ₹", 300, 2000, 2000, 50, key="fl_fare")
    with fc2:
        f_rat = st.slider("Min Rating ⭐", 3.0, 5.0, 3.0, 0.1, key="fl_rat")
    with fd:
        f_sort = st.selectbox("Sort By",
            ["Recommended","Fare ↑","Fare ↓","Rating ↓","Departure ↑"], key="fl_sort")

    st.markdown('<div class="sp"></div>', unsafe_allow_html=True)

    fl = [b for b in BUSES if
          (not f_type or b["type"] in f_type) and
          b["fare"] <= f_fare and b["rating"] >= f_rat]
    if f_sort == "Fare ↑":      fl.sort(key=lambda x: x["fare"])
    elif f_sort == "Fare ↓":    fl.sort(key=lambda x: -x["fare"])
    elif f_sort == "Rating ↓":  fl.sort(key=lambda x: -x["rating"])
    elif f_sort == "Departure ↑": fl.sort(key=lambda x: x["dep"])

    if not fl:
        st.info("No buses match your filters. Try adjusting them.")

    for bus in fl:
        type_cls = "ac" if "AC" in bus["type"] else "eco"
        if "Sleeper" in bus["type"] or "Multi" in bus["type"]: type_cls = "sleeper"
        cat_cls = bus["cat"]
        stars = "★" * int(bus["rating"]) + "☆" * (5 - int(bus["rating"]))
        chip_html = "".join(f'<span class="bca-chip">{a}</span>' for a in bus["amenities"])
        seats_col = "#ef4444" if bus["seats"] < 10 else "#10b981"
        hurry = "⚡ Only a few left!" if bus["seats"] < 10 else ""
        save = bus["old"] - bus["fare"]

        st.markdown(f"""
        <div class="bus-card-adv {cat_cls}">
          <div class="bca-top">
            <div>
              <div class="bca-name">{bus['name']}</div>
              <div class="bca-type {type_cls}">{bus['type']}</div>
              <div class="bca-rating" style="margin-top:8px">{stars} <span style="color:rgba(255,255,255,0.4)">{bus['rating']}</span></div>
            </div>
            <div class="bca-fare">
              <div class="bca-oldp">₹{bus['old']:,}</div>
              <div class="bca-price">₹{bus['fare']:,}<span style="font-size:12px;color:rgba(255,255,255,0.4)">/seat</span></div>
              <div class="bca-save">💚 Save ₹{save:,}</div>
            </div>
          </div>
          <div class="bca-route">
            <div>
              <div class="bca-time">{bus['dep']}</div>
              <div class="bca-city">{st.session_state.src}</div>
            </div>
            <div class="bca-line">
              <div class="bca-dots">
                <div class="bca-dot"></div>
                <div class="bca-seg"></div>
                <div class="bca-dot"></div>
              </div>
              <div class="bca-dur">{bus['dur']}</div>
            </div>
            <div style="text-align:right">
              <div class="bca-time">{bus['arr']}</div>
              <div class="bca-city">{st.session_state.dst}</div>
            </div>
          </div>
          <div class="bca-bottom">
            <div class="bca-amenities">{chip_html}</div>
            <div class="bca-seats">
              <div class="bca-seats-n" style="color:{seats_col}">{bus['seats']}</div>
              <div class="bca-seats-l">seats left</div>
              <div style="font-size:10px;color:#ef4444;font-weight:700;margin-top:2px">{hurry}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        bc1, bc2, bc3 = st.columns([3, 1, 1])
        with bc3:
            if st.button("Select Seats →", key=f"pick_{bus['id']}"):
                st.session_state.selected_bus = bus
                st.session_state.selected_seats = []
                st.session_state["active_nav"] = "💺 Seat Selector"
                st.rerun()
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — SEAT SELECTOR
# ══════════════════════════════════════════════════════════════════════════════
elif active_nav == "💺 Seat Selector":
    bus = st.session_state.selected_bus or BUSES[0]
    sel = st.session_state.selected_seats

    st.markdown('<div class="sec">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sec-hdr">
      <div>
        <div class="sec-title">💺 Seat Selector — <span>{bus['name']}</span></div>
        <div class="sec-sub">{bus['type']} &nbsp;·&nbsp; {bus['dep']} → {bus['arr']} &nbsp;·&nbsp; {bus['dur']}</div>
      </div>
      <div>
        <span style="font-family:'Space Grotesk',sans-serif;font-size:28px;font-weight:800;color:#ef4444">₹{bus['fare']:,}</span>
        <span style="font-size:12px;color:rgba(255,255,255,0.4)"> / seat</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([3, 2])

    with left:
        # Legend
        st.markdown("""
        <div class="seat-legend">
          <div class="sleg"><div class="sleg-sq" style="background:rgba(16,185,129,0.2);border:1.5px solid #10b981"></div>Available</div>
          <div class="sleg"><div class="sleg-sq" style="background:#ef4444"></div>Selected</div>
          <div class="sleg"><div class="sleg-sq" style="background:rgba(255,255,255,0.08);border:1.5px solid rgba(255,255,255,0.15)"></div>Booked</div>
          <div class="sleg"><div class="sleg-sq" style="background:rgba(236,72,153,0.2);border:1.5px solid #ec4899"></div>Ladies Only</div>
        </div>
        """, unsafe_allow_html=True)

        for deck_name, layout in [("🔽 Lower Deck", LOWER), ("🔼 Upper Deck", UPPER)]:
            st.markdown(f"""
            <div class="seat-wrapper">
              <div class="deck-title">{deck_name}</div>
              <div class="bus-nose">🚌 &nbsp; DRIVER CABIN &nbsp; ·&nbsp; {bus['name'].upper()}</div>
            """, unsafe_allow_html=True)

            for row in layout:
                cols = st.columns([1,1,0.5,1,1])
                for i, sid in enumerate(row):
                    with cols[i]:
                        if sid == "":
                            st.write("")
                        elif sid in BOOKED:
                            st.markdown(f"""
                            <div style="background:rgba(255,255,255,0.05);border:1.5px solid rgba(255,255,255,0.1);
                            border-radius:10px;height:46px;display:flex;align-items:center;
                            justify-content:center;font-size:10px;color:rgba(255,255,255,0.2);
                            font-weight:600">❌</div>
                            """, unsafe_allow_html=True)
                        elif sid in LADIES:
                            lbl = f"♀ {sid}"
                            if st.button(lbl, key=f"s_{sid}"):
                                if sid in sel: sel.remove(sid)
                                else: sel.append(sid)
                                st.session_state.selected_seats = sel
                        else:
                            lbl = f"✓ {sid}" if sid in sel else sid
                            if st.button(lbl, key=f"s_{sid}"):
                                if sid in sel: sel.remove(sid)
                                else: sel.append(sid)
                                st.session_state.selected_seats = sel

            st.markdown('</div>', unsafe_allow_html=True)

    with right:
        # Booking summary
        cnt   = len(sel)
        fare  = bus["fare"] * cnt
        tax   = int(fare * 0.05)
        grand = fare + tax
        seats_str = ", ".join(sel) if sel else "— None selected"
        col_v = "#fbbf24" if sel else "rgba(255,255,255,0.3)"

        st.markdown(f"""
        <div class="booking-glass">
          <div class="bp-title">🎟 Booking Summary</div>
          <div class="bp-row"><span class="bp-k">Route</span><span class="bp-v">{st.session_state.src} → {st.session_state.dst}</span></div>
          <div class="bp-row"><span class="bp-k">Bus</span><span class="bp-v">{bus['name']}</span></div>
          <div class="bp-row"><span class="bp-k">Type</span><span class="bp-v">{bus['type']}</span></div>
          <div class="bp-row"><span class="bp-k">Time</span><span class="bp-v">{bus['dep']} → {bus['arr']}</span></div>
          <div class="bp-row"><span class="bp-k">Selected Seats</span><span class="bp-v" style="color:{col_v}">{seats_str}</span></div>
          <div class="bp-row"><span class="bp-k">Seat Count</span><span class="bp-v">{cnt}</span></div>
          <div class="bp-row"><span class="bp-k">Base Fare</span><span class="bp-v">₹{bus['fare']:,} × {cnt} = ₹{fare:,}</span></div>
          <div class="bp-row"><span class="bp-k">GST (5%)</span><span class="bp-v">+ ₹{tax:,}</span></div>
          <div class="bp-total">
            <div class="bp-total-l">TOTAL PAYABLE</div>
            <div class="bp-total-v">₹{grand:,}</div>
            <div class="bp-total-t">{cnt} seat(s) · incl. all taxes</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sp"></div>', unsafe_allow_html=True)
        st.markdown("#### 👤 Passenger Details")

        nm  = st.text_input("Full Name *", value=st.session_state.passenger_name, key="pf_name")
        mob = st.text_input("Mobile *", value=st.session_state.passenger_mobile, key="pf_mob")
        eml = st.text_input("Email", value=st.session_state.passenger_email, key="pf_eml")
        gen = st.radio("Gender", ["Male","Female","Other"], horizontal=True, key="pf_gen")
        age = st.number_input("Age", 5, 100, 25, key="pf_age")

        st.markdown('<div class="sp"></div>', unsafe_allow_html=True)

        can_book = len(sel) > 0 and nm.strip() and mob.strip()
        if st.button("💳  Confirm & Pay Now", key="btn_confirm", disabled=not can_book):
            st.session_state.passenger_name   = nm
            st.session_state.passenger_mobile = mob
            st.session_state.passenger_email  = eml
            with st.spinner("⏳ Securing your seats…"):
                time.sleep(1.4)
            pnr = f"RB-{random.randint(10000000,99999999)}"
            st.session_state.confirmed_pnr = pnr
            st.balloons()
            st.success(f"🎉 **Confirmed!** PNR `{pnr}` — see your ticket on the 🏠 Home tab!")

        if not sel:
            st.info("👆 Select at least one seat from the map to proceed.")

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — AI ASSISTANT
# ══════════════════════════════════════════════════════════════════════════════
elif active_nav == "🤖 AI Assistant":
    st.markdown('<div class="sec">', unsafe_allow_html=True)

    al, ar = st.columns([3, 2])

    with al:
        if st.session_state.agent is None:
            try:
                st.session_state.agent = RedBusConversationalAgent()
            except Exception:
                pass

        if not st.session_state.chat_history:
            st.session_state.chat_history = [("bot",
                "👋 Hi! I'm your RedBus AI assistant.\n\n"
                "I can help you:\n• Find buses & compare fares\n• Predict ticket prices\n"
                "• Recommend best routes\n• Answer travel queries\n\n"
                "Try: *'Find AC sleeper from Chennai to Bangalore tomorrow night'*")]

        st.markdown("""
        <div class="chat-wrap">
          <div class="chat-hdr">
            <div class="chat-av">🤖</div>
            <div>
              <div class="chat-name">RedBus AI Assistant</div>
              <div class="chat-status"><div class="live-dot"></div> Online · NLP + ML Powered</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        msgs_html = '<div class="chat-msgs">'
        for role, msg in st.session_state.chat_history[-14:]:
            msgs_html += f'<div class="msg {role}"><div class="bubble {role}">{msg}</div></div>'
        msgs_html += '</div>'
        st.markdown(msgs_html, unsafe_allow_html=True)

        ci, cb = st.columns([5,1])
        with ci:
            ui = st.text_input("", placeholder="Ask me anything…", label_visibility="collapsed", key="ai_inp")
        with cb:
            send = st.button("Send", key="ai_snd")

        # Quick prompts
        qc = st.columns(4)
        quick = ["🌙 Night buses","💰 Cheapest","⭐ Top rated","🛏️ Sleeper AC"]
        for i, (c, q) in enumerate(zip(qc, quick)):
            with c:
                if st.button(q, key=f"q_{i}"):
                    ui = q; send = True

        if send and ui.strip():
            st.session_state.chat_history.append(("user", ui))
            try:
                resp = st.session_state.agent.chat(ui) if st.session_state.agent else None
                if not resp: raise Exception("No agent")
            except Exception as e:
                info = "\n".join([f"• **{b['name']}** — ₹{b['fare']} | {b['type']} | ⭐{b['rating']}" for b in BUSES[:3]])
                resp = f"Here are top buses I found:\n\n{info}\n\n*(Error: {str(e)[:60]})*"
            st.session_state.chat_history.append(("bot", resp))
            st.rerun()

    with ar:
        st.markdown("#### 📈 7-Day Fare Forecast")
        try:
            analytics = BusPriceAnalytics()
            days  = [(datetime.today()+timedelta(days=i)).strftime("%d %b") for i in range(7)]
            prices = [analytics.predict_price(st.session_state.src, st.session_state.dst, i) for i in range(7)]
        except Exception:
            days   = [(datetime.today()+timedelta(days=i)).strftime("%d %b") for i in range(7)]
            prices = [750,820,780,950,1100,1250,890]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=days, y=prices, mode='lines+markers',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=9, color='#fbbf24', line=dict(color='#ef4444',width=2)),
            fill='tozeroy', fillcolor='rgba(220,38,38,0.08)', name="Forecast"
        ))
        fig.update_layout(
            height=240, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, tickfont=dict(color='rgba(255,255,255,0.5)',size=11)),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)',
                       tickprefix='₹', tickfont=dict(color='rgba(255,255,255,0.5)',size=11)),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🕸️ Bus Comparison Radar")
        try:
            radar = BusComparator.compare(BUSES[:3])
            radar.update_layout(
                height=280, margin=dict(l=20,r=20,t=20,b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                polar=dict(
                    bgcolor='rgba(255,255,255,0.03)',
                    angularaxis=dict(tickfont=dict(size=10, color='rgba(255,255,255,0.7)'),
                                     gridcolor='rgba(255,255,255,0.08)'),
                    radialaxis=dict(gridcolor='rgba(255,255,255,0.08)',
                                    tickfont=dict(color='rgba(255,255,255,0.4)', size=9),
                                    linecolor='rgba(255,255,255,0.1)'))
            )
            st.plotly_chart(radar, use_container_width=True)
        except Exception:
            cats = ['Comfort','Value','Speed','Rating','Amenities']
            fig2 = go.Figure()
            palette = ['#ef4444','#fbbf24','#10b981']
            for bus2, clr in zip(BUSES[:3], palette):
                sc = [bus2["rating"]*2, (2000-bus2["fare"])/400,
                      9-int(bus2["dur"][0]), bus2["rating"]*2, len(bus2["amenities"])]
                fig2.add_trace(go.Scatterpolar(
                    r=sc+[sc[0]], theta=cats+[cats[0]],
                    fill='toself', name=bus2['name'],
                    line=dict(color=clr, width=2), opacity=0.75
                ))
            fig2.update_layout(
                height=280, margin=dict(l=20,r=20,t=20,b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                polar=dict(bgcolor='rgba(255,255,255,0.03)',
                           angularaxis=dict(tickcolor='rgba(255,255,255,0.3)',
                                            gridcolor='rgba(255,255,255,0.08)',
                                            linecolor='rgba(255,255,255,0.1)'),
                           radialaxis=dict(gridcolor='rgba(255,255,255,0.08)',
                                           tickfont=dict(color='rgba(255,255,255,0.4)',size=9),
                                           linecolor='rgba(0,0,0,0)')),
                legend=dict(font=dict(size=11,color='rgba(255,255,255,0.6)'),
                            bgcolor='rgba(0,0,0,0)')
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif active_nav == "📊 Dashboard":
    st.markdown('<div class="sec">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-hdr">
      <div><div class="sec-title">Platform <span>Dashboard</span></div>
      <div class="sec-sub">Live analytics · Updated every 60 seconds</div></div>
      <div class="sec-pill">📊 Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    st.markdown("""
    <div class="kpi-row">
      <div class="kpi-card red">
        <div class="kpi-icon">🎫</div>
        <div class="kpi-num">1,284</div>
        <div class="kpi-label">Tickets Booked Today</div>
        <div class="kpi-trend up">↑ +12.4% vs yesterday</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-icon">💰</div>
        <div class="kpi-num">₹9.2L</div>
        <div class="kpi-label">Revenue (Today)</div>
        <div class="kpi-trend up">↑ +8.7% week-on-week</div>
      </div>
      <div class="kpi-card blue">
        <div class="kpi-icon">🚌</div>
        <div class="kpi-num">847</div>
        <div class="kpi-label">Active Routes</div>
        <div class="kpi-trend up">↑ +3 new routes added</div>
      </div>
      <div class="kpi-card amber">
        <div class="kpi-icon">⭐</div>
        <div class="kpi-num">4.86</div>
        <div class="kpi-label">Avg User Rating</div>
        <div class="kpi-trend up">↑ +0.02 this week</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sp"></div>', unsafe_allow_html=True)

    da, db = st.columns([3,2])

    with da:
        st.markdown("#### 📅 Booking Trend — 30 Days")
        dates = [(datetime.today()-timedelta(days=29-i)).strftime("%d %b") for i in range(30)]
        bkgs  = [random.randint(900,1400) for _ in range(30)]
        rev   = [b*random.randint(700,900)//1000 for b in bkgs]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=dates, y=bkgs, name="Bookings",
            marker_color='rgba(220,38,38,0.6)',
            marker_line=dict(color='#ef4444', width=0.5)))
        fig.add_trace(go.Scatter(x=dates, y=rev, name="Revenue ₹K",
            mode='lines', yaxis='y2',
            line=dict(color='#fbbf24', width=2.5)))
        fig.update_layout(
            height=320, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, tickangle=-40,
                       tickfont=dict(color='rgba(255,255,255,0.4)',size=10)),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)',
                       tickfont=dict(color='rgba(255,255,255,0.4)',size=11)),
            yaxis2=dict(overlaying='y', side='right',
                        tickprefix='₹', showgrid=False,
                        tickfont=dict(color='rgba(255,255,255,0.4)',size=11)),
            legend=dict(orientation='h', y=1.05,
                        font=dict(color='rgba(255,255,255,0.6)',size=11),
                        bgcolor='rgba(0,0,0,0)'),
            bargap=0.3
        )
        st.plotly_chart(fig, use_container_width=True)

    with db:
        st.markdown("#### 🗺️ Top Routes")
        routes = ["Chennai→Blr","Mumbai→Pune","Delhi→Jaipur","Hyd→Vizag","Coimbatore→Chn"]
        counts = [4280,3650,2970,2410,1890]
        fig2 = go.Figure(go.Bar(
            y=routes, x=counts, orientation='h',
            marker=dict(color=['#ef4444','#f87171','#fca5a5','#fecaca','#fee2e2'],
                        line=dict(width=0)),
            text=[f"{c:,}" for c in counts],
            textposition='outside',
            textfont=dict(size=11, color='rgba(255,255,255,0.6)')
        ))
        fig2.update_layout(
            height=320, margin=dict(l=0,r=60,t=0,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, tickfont=dict(color='rgba(255,255,255,0.6)',size=12))
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="sp"></div>', unsafe_allow_html=True)

    # Heatmap
    st.markdown("#### 🌡️ Seat Occupancy Heatmap by Hour")
    days_w = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    hours  = [f"{h:02d}:00" for h in range(6,24,2)]
    occ    = np.random.randint(20, 100, (len(days_w), len(hours)))
    fig3   = go.Figure(go.Heatmap(
        z=occ, x=hours, y=days_w,
        colorscale=[[0,'rgba(220,38,38,0.05)'],[0.5,'rgba(220,38,38,0.4)'],[1,'#ef4444']],
        showscale=True, colorbar=dict(title="Occ%",
            tickfont=dict(color='rgba(255,255,255,0.5)',size=10)),
        text=[[f"{v}%" for v in r] for r in occ],
        texttemplate="%{text}", textfont=dict(size=10,color='rgba(255,255,255,0.8)')
    ))
    fig3.update_layout(
        height=280, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickfont=dict(color='rgba(255,255,255,0.5)',size=11)),
        yaxis=dict(tickfont=dict(color='rgba(255,255,255,0.5)',size=11))
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="sp"></div>', unsafe_allow_html=True)

    # ML metrics
    mc = st.columns(4)
    for col, name, val, unit, clr in [
        (mc[0],"Price Forecast R²","0.912","","#3b82f6"),
        (mc[1],"Recommendation Acc","94.3","%","#10b981"),
        (mc[2],"Intent Parse Acc","96.7","%","#ef4444"),
        (mc[3],"Response Time","0.28","s","#fbbf24"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="text-align:center;padding:20px">
              <div style="font-size:11px;color:rgba(255,255,255,0.4);letter-spacing:1px;text-transform:uppercase">{name}</div>
              <div style="font-family:'Space Grotesk',sans-serif;font-size:30px;font-weight:800;color:{clr};margin:10px 0">
                {val}<span style="font-size:14px;color:rgba(255,255,255,0.4)">{unit}</span></div>
              <div style="height:3px;background:linear-gradient(90deg,{clr},{clr}33);border-radius:2px"></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — TEST LAB
# ══════════════════════════════════════════════════════════════════════════════
elif active_nav == "⚡ Test Lab":
    st.markdown('<div class="sec">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-hdr">
      <div>
        <div class="sec-title">⚡ SDET <span>Test Lab</span></div>
        <div class="sec-sub">Selenium · PyTest · Page Object Model · AI Test Suite</div>
      </div>
      <div class="sec-pill">9 Test Cases</div>
    </div>
    """, unsafe_allow_html=True)

    suites = [
        {"ico":"🔁","name":"E2E Booking Flow",    "desc":"Full booking: search → seat → passenger → confirm",
         "mod":"tests/test_redbus_e2e_booking.py", "n":4},
        {"ico":"🤖","name":"AI Booking Assistant","desc":"NLP intent, recommender, price ML, conversational agent",
         "mod":"tests/test_ai_booking_assistant.py","n":6},
        {"ico":"🔍","name":"Search & Filters",    "desc":"Route search, fare filter, departure, seat availability",
         "mod":"tests/test_redbus_search.py",      "n":5},
    ]

    for s in suites:
        res = st.session_state.test_results.get(s["mod"], "idle")
        bcls = {"pass":"pass","fail":"fail","running":"run","idle":"idle"}.get(res,"idle")
        btxt = {"pass":"✅ PASSED","fail":"❌ FAILED","running":"⏳ RUNNING","idle":"· IDLE"}.get(res,"· IDLE")

        st.markdown(f"""
        <div class="test-suite-card">
          <div class="ts-icon">{s['ico']}</div>
          <div class="ts-info">
            <div class="ts-name">{s['name']}</div>
            <div class="ts-desc">{s['desc']} &nbsp;·&nbsp; {s['n']} test cases</div>
            <div class="ts-path">{s['mod']}</div>
          </div>
          <div class="ts-badge {bcls}">{btxt}</div>
        </div>
        """, unsafe_allow_html=True)

        rc1, rc2 = st.columns([5,1])
        with rc2:
            if st.button("▶ Run", key=f"r_{s['mod']}"):
                st.session_state.test_results[s["mod"]] = "running"
                st.rerun()

        if res == "running":
            with st.spinner(f"Running {s['name']}…"):
                try:
                    r = subprocess.run(
                        ["python","-m","pytest", s["mod"], "-v","--tb=short",
                         "--html=reports/report.html","--self-contained-html"],
                        capture_output=True, text=True, cwd=BASE_DIR, timeout=120)
                    ok = r.returncode == 0
                    st.session_state.test_results[s["mod"]] = "pass" if ok else "fail"
                    out = (r.stdout + r.stderr)[-3500:]
                    st.markdown(f'<div class="terminal">{out}</div>', unsafe_allow_html=True)
                    if ok: st.success(f"✅ {s['name']} — All tests PASSED!")
                    else:  st.error(f"❌ {s['name']} — Some tests FAILED")
                except Exception as ex:
                    st.session_state.test_results[s["mod"]] = "fail"
                    st.error(f"Runner error: {ex}")
            st.rerun()

    st.markdown('<div class="sp"></div>', unsafe_allow_html=True)

    rall, rdl = st.columns(2)
    with rall:
        if st.button("🚀  Run ALL 9 Tests", key="run_all_btn"):
            for s in suites:
                st.session_state.test_results[s["mod"]] = "running"
            with st.spinner("⏳ Running full test suite…"):
                try:
                    r = subprocess.run(
                        ["python","-m","pytest","tests/","-v","--tb=short",
                         "--html=reports/report.html","--self-contained-html"],
                        capture_output=True, text=True, cwd=BASE_DIR, timeout=200)
                    ok = r.returncode == 0
                    for s in suites:
                        st.session_state.test_results[s["mod"]] = "pass" if ok else "fail"
                    st.markdown(f'<div class="terminal">{(r.stdout+r.stderr)[-4000:]}</div>', unsafe_allow_html=True)
                    if ok:
                        st.balloons()
                        st.success("🎉 ALL 9 TESTS PASSED — 100% Pass Rate!")
                    else:
                        st.error("❌ Some tests failed")
                except Exception as ex:
                    st.error(f"Error: {ex}")

    with rdl:
        rp = BASE_DIR / "reports" / "report.html"
        if rp.exists():
            with open(rp,"rb") as f:
                st.download_button("📊  Download HTML Report", f,
                    "test_report.html","text/html",key="dl_rep")
        else:
            st.info("📊 Run tests first to generate report")

    # Architecture treemap
    st.markdown('<div class="sp"></div>', unsafe_allow_html=True)
    st.markdown("#### 🏗️ Test Architecture Map")
    fig_arch = go.Figure(go.Treemap(
        labels=["Framework","E2E","AI Suite","Search",
                "Selenium","PageObjects","Conftest",
                "IntentParser","Recommender","PriceML","ConvAgent",
                "RouteSearch","FareFilter","SeatCheck"],
        parents=["","Framework","Framework","Framework",
                 "E2E","E2E","E2E",
                 "AI Suite","AI Suite","AI Suite","AI Suite",
                 "Search","Search","Search"],
        values=[1]*14,
        marker_colors=["#0d0f1a","#ef4444","#3b82f6","#10b981",
                       "#f87171","#fca5a5","#fee2e2",
                       "#60a5fa","#93c5fd","#bfdbfe","#dbeafe",
                       "#6ee7b7","#a7f3d0","#d1fae5"],
        textfont=dict(size=12, color='white'),
        pathbar=dict(visible=False)
    ))
    fig_arch.update_layout(
        height=320, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_arch, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
