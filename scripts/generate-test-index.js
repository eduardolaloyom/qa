#!/usr/bin/env node

/**
 * Script para generar índice de reportes históricos de Playwright
 * Se ejecuta post-tests para actualizar public/reports-history.json
 * Usado por GitHub Pages para mostrar histórico de salud
 */

const fs = require('fs');
const path = require('path');

const REPORTS_DIR = path.join(__dirname, '../public');
const HISTORY_FILE = path.join(REPORTS_DIR, 'reports-history.json');

interface TestResult {
  name: string;
  timestamp: string;
  passed: number;
  failed: number;
  skipped: number;
  duration: number;
  url: string;
}

function parsePlaywrightReport(jsonFile) {
  if (!fs.existsSync(jsonFile)) {
    return null;
  }

  try {
    const data = JSON.parse(fs.readFileSync(jsonFile, 'utf-8'));
    const stats = data.stats || {};

    return {
      passed: stats.expected || 0,
      failed: stats.unexpected || 0,
      skipped: stats.skipped || 0,
      duration: stats.duration || 0,
    };
  } catch (e) {
    console.error(`Error parsing ${jsonFile}:`, e.message);
    return null;
  }
}

function updateHistory() {
  const now = new Date().toISOString();
  const timestamp = new Date().toLocaleString('es-CL', {
    dateStyle: 'short',
    timeStyle: 'short',
    timeZone: 'America/Santiago',
  });

  let history = [];
  if (fs.existsSync(HISTORY_FILE)) {
    try {
      history = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf-8'));
    } catch (e) {
      console.warn('Could not parse history file, starting fresh');
    }
  }

  // Procesar reportes de Codelpa y Surtiventas
  const clients = ['codelpa', 'surtiventas'];

  for (const client of clients) {
    const jsonFile = path.join(REPORTS_DIR, client, 'index.json');
    const results = parsePlaywrightReport(jsonFile);

    if (results) {
      const entry = {
        client,
        timestamp,
        iso: now,
        passed: results.passed,
        failed: results.failed,
        skipped: results.skipped,
        duration: results.duration,
        health: Math.round((results.passed / (results.passed + results.failed || 1)) * 100),
        reportUrl: `./${client}/index.html`,
      };

      // Mantener últimos 30 reportes por cliente
      history = history.filter(e => e.client !== client);
      history.push(entry);
    }
  }

  // Ordenar por timestamp descendente
  history.sort((a, b) => new Date(b.iso).getTime() - new Date(a.iso).getTime());

  // Mantener últimos 60 registros totales
  history = history.slice(0, 60);

  fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2));
  console.log(`✅ Updated reports history: ${history.length} entries`);
}

updateHistory();
