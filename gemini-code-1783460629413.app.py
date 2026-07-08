<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inteligencia de Campañas | Loterías</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- ApexCharts para gráficos profesionales -->
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#1e3a8a', // Blue 900
                        secondary: '#3b82f6', // Blue 500
                        accent: '#10b981', // Emerald 500
                        danger: '#ef4444', // Red 500
                        warning: '#f59e0b', // Amber 500
                        surface: '#ffffff',
                        background: '#f8fafc'
                    },
                    fontFamily: {
                        sans: ['Inter', 'system-ui', 'sans-serif'],
                    }
                }
            }
        }
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .card { background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
        .glass { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); }
        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #f1f1f1; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
</head>
<body class="text-slate-800 antialiased min-h-screen flex flex-col">

    <!-- Top Navigation -->
    <header class="glass sticky top-0 z-50 border-b border-slate-200 px-6 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-primary text-white rounded-lg flex items-center justify-center text-xl shadow-md">
                <i class="fa-solid fa-chart-pie"></i>
            </div>
            <div>
                <h1 class="text-xl font-bold text-slate-900 leading-tight">Dashboard Ejecutivo</h1>
                <p class="text-xs text-slate-500 font-medium">Analítica de Actividad & Insights</p>
            </div>
        </div>
        <div class="flex gap-4 items-center">
            <div class="text-sm font-medium text-slate-600 bg-slate-100 px-3 py-1.5 rounded-md border border-slate-200 flex items-center gap-2">
                <i class="fa-regular fa-calendar"></i>
                <span id="date-range-label">Últimos 14 Días</span>
            </div>
            <button class="bg-primary hover:bg-blue-800 text-white text-sm font-medium px-4 py-2 rounded-md transition-colors shadow-sm" onclick="alert('En producción, esto abriría un modal para subir el archivo Excel.')">
                <i class="fa-solid fa-upload mr-2"></i> Subir Datos
            </button>
        </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 p-6 max-w-[1600px] mx-auto w-full flex flex-col gap-6">
        
        <!-- KPIs Section -->
        <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="card p-5 relative overflow-hidden">
                <div class="absolute top-0 right-0 p-4 opacity-10 text-primary text-5xl"><i class="fa-solid fa-paper-plane"></i></div>
                <h3 class="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Volumen Impactado</h3>
                <div class="text-3xl font-bold text-slate-800" id="kpi-envios">0</div>
                <div class="mt-2 text-xs font-medium text-slate-500">Total de envíos procesados</div>
            </div>
            <div class="card p-5 relative overflow-hidden">
                <div class="absolute top-0 right-0 p-4 opacity-10 text-accent text-5xl"><i class="fa-solid fa-users"></i></div>
                <h3 class="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Clientes Activos</h3>
                <div class="text-3xl font-bold text-slate-800" id="kpi-jugadores">0</div>
                <div class="mt-2 text-xs font-medium text-accent"><i class="fa-solid fa-arrow-trend-up mr-1"></i> Principal métrica de conversión</div>
            </div>
            <div class="card p-5 relative overflow-hidden border-l-4 border-l-accent">
                <div class="absolute top-0 right-0 p-4 opacity-10 text-accent text-5xl"><i class="fa-solid fa-bolt"></i></div>
                <h3 class="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-1">Tasa de Actividad</h3>
                <div class="text-3xl font-bold text-accent" id="kpi-tasa">0.00%</div>
                <div class="mt-2 text-xs font-medium text-slate-500">Conversión global promedio</div>
            </div>
            <div class="card p-5 bg-gradient-to-br from-primary to-blue-700 text-white">
                <h3 class="text-sm font-medium text-blue-200 uppercase tracking-wider mb-1">Mix Ganador</h3>
                <div class="text-2xl font-bold mb-1" id="kpi-mix-name">Calculando...</div>
                <div class="flex items-center gap-2 mt-2 bg-white/20 rounded px-2 py-1 w-fit">
                    <i class="fa-solid fa-star text-yellow-300 text-xs"></i>
                    <span class="text-sm font-semibold" id="kpi-mix-tasa">0%</span>
                </div>
            </div>
        </section>

        <!-- Insights Section -->
        <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="card p-6 border-t-4 border-t-warning">
                <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2 mb-4">
                    <i class="fa-solid fa-lightbulb text-warning"></i> Análisis Semántico & Recomendaciones
                </h2>
                <div class="space-y-4">
                    <div class="flex gap-4 items-start">
                        <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center shrink-0 mt-1"><i class="fa-solid fa-comment-dots"></i></div>
                        <div>
                            <h4 class="font-semibold text-slate-800 text-sm">El Gatillo Ganador</h4>
                            <p class="text-sm text-slate-600 mt-1" id="insight-keyword">Cargando análisis semántico...</p>
                        </div>
                    </div>
                    <div class="flex gap-4 items-start">
                        <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0 mt-1"><i class="fa-solid fa-link"></i></div>
                        <div>
                            <h4 class="font-semibold text-slate-800 text-sm">Fricción en Redirección</h4>
                            <p class="text-sm text-slate-600 mt-1">Incluir URLs cortas (cutt.ly) y CTA claros ('Juega aquí') en los primeros 40 caracteres incrementa la actividad en SMS/WA.</p>
                        </div>
                    </div>
                    <div class="bg-slate-50 p-3 rounded-lg border border-slate-200 mt-2">
                        <span class="text-xs font-bold uppercase text-slate-500 mb-1 block">Sugerencia de Copy (Próxima Semana)</span>
                        <p class="text-sm italic text-slate-700">"Priorizar la urgencia y el incentivo económico ('pozo', 'gratis') en las dos primeras líneas."</p>
                    </div>
                </div>
            </div>

            <div class="card p-6 border-t-4 border-t-primary">
                <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2 mb-4">
                    <i class="fa-solid fa-rocket text-primary"></i> Plan de Acción (Últimos 14 Días)
                </h2>
                <ul class="space-y-4">
                    <li class="flex gap-3">
                        <i class="fa-solid fa-bullseye text-primary mt-1"></i>
                        <div>
                            <span class="font-semibold text-sm block">Foco de Producto</span>
                            <span class="text-sm text-slate-600" id="insight-producto">Destinar mayor volumen de envíos a las verticales con picos recientes de actividad.</span>
                        </div>
                    </li>
                    <li class="flex gap-3">
                        <i class="fa-solid fa-tower-cell text-primary mt-1"></i>
                        <div>
                            <span class="font-semibold text-sm block">Canal Prioritario</span>
                            <span class="text-sm text-slate-600" id="insight-canal">Liderando la conversión. Usar como vía principal para segmentos VIP.</span>
                        </div>
                    </li>
                    <li class="flex gap-3">
                        <i class="fa-solid fa-shield-halved text-primary mt-1"></i>
                        <div>
                            <span class="font-semibold text-sm block">Manejo de Fatiga</span>
                            <span class="text-sm text-slate-600">Rotar segmentos en canales tradicionales (Mail/SMS) para evitar quemar la base. Apoyarse en triggers de saldo automático.</span>
                        </div>
                    </li>
                </ul>
            </div>
        </section>

        <!-- Charts Section -->
        <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="card p-6">
                <h2 class="text-lg font-bold text-slate-800 mb-1">Rendimiento por Canal</h2>
                <p class="text-xs text-slate-500 mb-4">Tasa de actividad promedio (%)</p>
                <div id="chart-channels" class="w-full h-72"></div>
            </div>
            <div class="card p-6">
                <h2 class="text-lg font-bold text-slate-800 mb-1">Rendimiento por Producto</h2>
                <p class="text-xs text-slate-500 mb-4">Tasa de actividad promedio (%)</p>
                <div id="chart-products" class="w-full h-72"></div>
            </div>
        </section>
        
        <!-- Evolutivo Temporal -->
        <section class="card p-6">
            <h2 class="text-lg font-bold text-slate-800 mb-1">Evolución de Actividad en el Tiempo</h2>
            <p class="text-xs text-slate-500 mb-4">Tendencia diaria de actividad general</p>
            <div id="chart-timeline" class="w-full h-72"></div>
        </section>

        <!-- Data Tables Section -->
        <section class="grid grid-cols-1 xl:grid-cols-3 gap-6">
            
            <!-- Alertas Críticas (1 Column) -->
            <div class="card p-0 col-span-1 border-red-200 overflow-hidden flex flex-col">
                <div class="bg-red-50 p-4 border-b border-red-100 flex items-center justify-between">
                    <h2 class="text-md font-bold text-red-700 flex items-center gap-2">
                        <i class="fa-solid fa-triangle-exclamation"></i> Alertas Críticas (< 1%)
                    </h2>
                    <span class="bg-red-200 text-red-800 text-xs font-bold px-2 py-1 rounded-full" id="alert-count">0</span>
                </div>
                <div class="p-0 overflow-auto flex-1 max-h-96">
                    <table class="w-full text-left border-collapse text-sm">
                        <thead class="bg-slate-50 sticky top-0">
                            <tr>
                                <th class="py-3 px-4 font-semibold text-slate-600 border-b">Campaña / Canal</th>
                                <th class="py-3 px-4 font-semibold text-slate-600 border-b text-right">Actividad</th>
                            </tr>
                        </thead>
                        <tbody id="alerts-table-body" class="divide-y divide-slate-100">
                            <!-- JS Injection -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Top 10 Campañas (2 Columns) -->
            <div class="card p-0 col-span-1 xl:col-span-2 overflow-hidden flex flex-col">
                <div class="bg-slate-50 p-4 border-b border-slate-200">
                    <h2 class="text-md font-bold text-slate-800 flex items-center gap-2">
                        <i class="fa-solid fa-trophy text-warning"></i> Top 10 Mejores Campañas
                    </h2>
                </div>
                <div class="p-0 overflow-auto flex-1 max-h-96">
                    <table class="w-full text-left border-collapse text-sm whitespace-nowrap">
                        <thead class="bg-slate-50 sticky top-0 z-10">
                            <tr>
                                <th class="py-3 px-4 font-semibold text-slate-600 border-b">Fecha</th>
                                <th class="py-3 px-4 font-semibold text-slate-600 border-b">Producto</th>
                                <th class="py-3 px-4 font-semibold text-slate-600 border-b">Canal</th>
                                <th class="py-3 px-4 font-semibold text-slate-600 border-b text-right">Impactos</th>
                                <th class="py-3 px-4 font-semibold text-slate-600 border-b text-right">Jugadores</th>
                                <th class="py-3 px-4 font-semibold text-slate-600 border-b text-right">Tasa Actividad</th>
                            </tr>
                        </thead>
                        <tbody id="top-table-body" class="divide-y divide-slate-100">
                            <!-- JS Injection -->
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

    </main>

    <!-- App Logic & Mock Data -->
    <script>
        // 1. MOCK DATA (Simulando el DataFrame de Pandas)
        // En producción, aquí se procesaría un archivo CSV/Excel mediante FileReader o API.
        const mockData = [
            { date: '2026-07-01', product: 'Tinka', channel: 'WHATSAPP', sends: 4500, players: 2100, message: '¡Juega HOY! El pozo está increíble. Gratis si participas.' },
            { date: '2026-07-02', product: 'Kábala', channel: 'SMS', sends: 12000, players: 4500, message: 'Revisa tu saldo, Kábala te espera. Juega aquí: cutt.ly/xyz' },
            { date: '2026-07-03', product: 'Tinka', channel: 'MAIL', sends: 55000, players: 120, message: 'Boletín informativo de la semana. Conoce los ganadores.' }, // Alerta crítica
            { date: '2026-07-04', product: 'Gana Diario', channel: 'SMS', sends: 8500, players: 3400, message: 'Tu bono vence hoy. Usa tu saldo y juega ya.' },
            { date: '2026-07-05', product: 'Casino', channel: 'WHATSAPP', sends: 2000, players: 900, message: 'Tiradas gratis en el nuevo slot. Entra ahora.' },
            { date: '2026-07-06', product: 'Tinka', channel: 'SMS', sends: 15000, players: 2500, message: 'El pozo millonario te llama. ¡No pierdas la oportunidad!' },
            { date: '2026-07-07', product: 'Kábala', channel: 'MAIL', sends: 30000, players: 250, message: 'Promoción especial para clientes inactivos. Regalo 1 jugada.' }, // Alerta
            { date: '2026-07-08', product: 'Te Apuesto', channel: 'SMS', sends: 18000, players: 6000, message: 'Apuesta en la final hoy. Cuotas mejoradas.' },
            { date: '2026-07-09', product: 'Tinka', channel: 'WHATSAPP', sends: 6000, players: 2800, message: '¡POZO HISTÓRICO! S/ 20 Millones. Juega ahora mismo gratis 1.' },
            { date: '2026-07-10', product: 'Gana Diario', channel: 'MAIL', sends: 40000, players: 300, message: 'Resumen de resultados de Gana Diario.' }, // Alerta
            { date: '2026-07-11', product: 'Casino', channel: 'SMS', sends: 10000, players: 2200, message: 'Bono de recarga activo. Doble saldo.' },
            { date: '2026-07-12', product: 'Tinka', channel: 'SMS', sends: 25000, players: 3000, message: 'Recupera tu suerte. Juega Tinka.' },
            { date: '2026-07-13', product: 'Kábala', channel: 'WHATSAPP', sends: 3500, players: 1500, message: 'Juega Kábala con tus números de la suerte. Juega aquí: bit.ly/kab' },
            { date: '2026-07-14', product: 'Te Apuesto', channel: 'SMS', sends: 22000, players: 7500, message: 'Champions League! Apuesta ya y gana.' },
        ];

        // Formatters
        const formatNumber = (num) => new Intl.NumberFormat('es-PE').format(num);
        const formatPercent = (num) => (num * 100).toFixed(2) + '%';

        // 2. CORE LOGIC (Simulando Pandas groupby y mean/sum)
        function processData(data) {
            let totalSends = 0;
            let totalPlayers = 0;
            
            const mixMap = {};
            const channelMap = {};
            const productMap = {};
            const timelineMap = {};
            const keywordsAnalysis = {
                'Urgencia/Tiempo': { words: ['hoy', 'ahora', 'ya'], sends: 0, players: 0 },
                'Gratuidad/Regalo': { words: ['gratis', 'regalo'], sends: 0, players: 0 },
                'Pozo/Millones': { words: ['pozo', 'millones'], sends: 0, players: 0 },
                'Redirección': { words: ['cutt.ly', 'bit.ly', 'juega aquí'], sends: 0, players: 0 },
            };

            data.forEach(row => {
                totalSends += row.sends;
                totalPlayers += row.players;
                
                // Mix (Product + Channel)
                const mixKey = `${row.product} | ${row.channel}`;
                if (!mixMap[mixKey]) mixMap[mixKey] = { sends: 0, players: 0, product: row.product, channel: row.channel };
                mixMap[mixKey].sends += row.sends;
                mixMap[mixKey].players += row.players;

                // Channel Grouping
                if (!channelMap[row.channel]) channelMap[row.channel] = { sends: 0, players: 0 };
                channelMap[row.channel].sends += row.sends;
                channelMap[row.channel].players += row.players;

                // Product Grouping
                if (!productMap[row.product]) productMap[row.product] = { sends: 0, players: 0 };
                productMap[row.product].sends += row.sends;
                productMap[row.product].players += row.players;
                
                // Timeline
                if (!timelineMap[row.date]) timelineMap[row.date] = { sends: 0, players: 0 };
                timelineMap[row.date].sends += row.sends;
                timelineMap[row.date].players += row.players;

                // Keyword Analysis
                const msg = row.message.toLowerCase();
                for (let category in keywordsAnalysis) {
                    if (keywordsAnalysis[category].words.some(w => msg.includes(w))) {
                        keywordsAnalysis[category].sends += row.sends;
                        keywordsAnalysis[category].players += row.players;
                    }
                }
            });

            return { totalSends, totalPlayers, mixMap, channelMap, productMap, timelineMap, keywordsAnalysis };
        }

        // 3. UI UPDATER
        function updateDashboard(data) {
            const metrics = processData(data);
            const globalRate = metrics.totalSends > 0 ? (metrics.totalPlayers / metrics.totalSends) : 0;

            // Update KPIs
            document.getElementById('kpi-envios').innerText = formatNumber(metrics.totalSends);
            document.getElementById('kpi-jugadores').innerText = formatNumber(metrics.totalPlayers);
            document.getElementById('kpi-tasa').innerText = formatPercent(globalRate);

            // Best Mix
            let bestMix = { key: '', rate: 0 };
            for (let k in metrics.mixMap) {
                let m = metrics.mixMap[k];
                let rate = m.sends > 0 ? (m.players / m.sends) : 0;
                if (rate > bestMix.rate && m.sends > 500) { // filter out low volume outliers
                    bestMix = { key: k, rate: rate };
                }
            }
            document.getElementById('kpi-mix-name').innerText = bestMix.key || 'N/A';
            document.getElementById('kpi-mix-tasa').innerText = formatPercent(bestMix.rate);

            // Insights - Best Keyword
            let bestKeyword = { name: '', rate: 0 };
            for (let k in metrics.keywordsAnalysis) {
                let cat = metrics.keywordsAnalysis[k];
                let rate = cat.sends > 0 ? (cat.players / cat.sends) : 0;
                if (rate > bestKeyword.rate) bestKeyword = { name: k, rate: rate };
            }
            document.getElementById('insight-keyword').innerHTML = `Textos con conceptos de <b>${bestKeyword.name}</b> promedian la mayor actividad (${formatPercent(bestKeyword.rate)}).`;

            // Insights - Best Prod/Chan (Simulating recent 14 days)
            let bestChan = { name: '', rate: 0 };
            for(let c in metrics.channelMap){
                let rate = metrics.channelMap[c].players / metrics.channelMap[c].sends;
                if(rate > bestChan.rate) bestChan = {name: c, rate: rate};
            }
            let bestProd = { name: '', rate: 0 };
            for(let p in metrics.productMap){
                let rate = metrics.productMap[p].players / metrics.productMap[p].sends;
                if(rate > bestProd.rate) bestProd = {name: p, rate: rate};
            }
            document.getElementById('insight-producto').innerHTML = `<b>${bestProd.name}</b> demostró el mayor pico de actividad recientemente.`;
            document.getElementById('insight-canal').innerHTML = `<b>${bestChan.name}</b> está liderando la conversión con un ${formatPercent(bestChan.rate)}.`;

            // Data for Charts
            const channelCategories = Object.keys(metrics.channelMap);
            const channelSeries = channelCategories.map(c => (metrics.channelMap[c].players / metrics.channelMap[c].sends * 100).toFixed(2));
            
            const productCategories = Object.keys(metrics.productMap);
            const productSeries = productCategories.map(p => (metrics.productMap[p].players / metrics.productMap[p].sends * 100).toFixed(2));

            const timelineCategories = Object.keys(metrics.timelineMap).sort();
            const timelineSeries = timelineCategories.map(d => (metrics.timelineMap[d].players / metrics.timelineMap[d].sends * 100).toFixed(2));

            // Render Charts
            renderBarChart('chart-channels', channelCategories, channelSeries, '#10b981'); // Emerald
            renderBarChart('chart-products', productCategories, productSeries, '#f59e0b'); // Amber
            renderLineChart('chart-timeline', timelineCategories, timelineSeries, '#3b82f6'); // Blue

            // Calculate Rates for rows and Sort for Tables
            const enrichedData = data.map(r => ({...r, rate: r.sends>0 ? (r.players/r.sends) : 0}));
            
            // Alerts Table (< 1% and > 500 sends)
            const alerts = enrichedData.filter(r => r.rate < 0.01 && r.sends > 500).sort((a,b) => a.rate - b.rate);
            document.getElementById('alert-count').innerText = alerts.length;
            const alertsHtml = alerts.map(a => `
                <tr class="hover:bg-red-50/50 transition-colors">
                    <td class="py-2 px-4 border-b">
                        <div class="font-medium text-slate-800">${a.product}</div>
                        <div class="text-xs text-slate-500">${a.channel} | ${formatNumber(a.sends)} envíos</div>
                    </td>
                    <td class="py-2 px-4 border-b text-right font-bold text-red-600">${formatPercent(a.rate)}</td>
                </tr>
            `).join('');
            document.getElementById('alerts-table-body').innerHTML = alerts.length ? alertsHtml : '<tr><td colspan="2" class="py-4 text-center text-slate-500">No hay alertas críticas.</td></tr>';

            // Top 10 Table
            const top10 = [...enrichedData].filter(r => r.sends > 500).sort((a,b) => b.rate - a.rate).slice(0, 10);
            const topHtml = top10.map(t => `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="py-2 px-4 border-b text-slate-600">${t.date}</td>
                    <td class="py-2 px-4 border-b font-medium text-slate-800">${t.product}</td>
                    <td class="py-2 px-4 border-b text-slate-600"><span class="bg-slate-100 px-2 py-1 rounded text-xs border border-slate-200">${t.channel}</span></td>
                    <td class="py-2 px-4 border-b text-right text-slate-600">${formatNumber(t.sends)}</td>
                    <td class="py-2 px-4 border-b text-right text-slate-600">${formatNumber(t.players)}</td>
                    <td class="py-2 px-4 border-b text-right font-bold text-accent">${formatPercent(t.rate)}</td>
                </tr>
            `).join('');
            document.getElementById('top-table-body').innerHTML = topHtml;
        }

        // 4. CHART SETUP (ApexCharts)
        let charts = {};
        function renderBarChart(elementId, categories, data, color) {
            if(charts[elementId]) charts[elementId].destroy();
            const options = {
                series: [{ name: 'Tasa Actividad', data: data }],
                chart: { type: 'bar', height: 280, toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
                plotOptions: { bar: { borderRadius: 4, horizontal: true, dataLabels: { position: 'top' } } },
                colors: [color],
                dataLabels: {
                    enabled: true,
                    offsetX: 25,
                    style: { fontSize: '11px', colors: ['#475569'], fontWeight: 600 },
                    formatter: function(val) { return val + "%" }
                },
                xaxis: { categories: categories, labels: { formatter: function(val) { return val + "%" } } },
                grid: { strokeDashArray: 4, borderColor: '#e2e8f0' }
            };
            charts[elementId] = new ApexCharts(document.querySelector("#" + elementId), options);
            charts[elementId].render();
        }

        function renderLineChart(elementId, categories, data, color) {
            if(charts[elementId]) charts[elementId].destroy();
            const options = {
                series: [{ name: 'Actividad General', data: data }],
                chart: { type: 'area', height: 280, toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
                colors: [color],
                fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05, stops: [0, 100] } },
                dataLabels: { enabled: false },
                stroke: { curve: 'smooth', width: 3 },
                xaxis: { categories: categories, tooltip: { enabled: false } },
                yaxis: { labels: { formatter: function(val) { return val + "%" } } },
                grid: { strokeDashArray: 4, borderColor: '#e2e8f0' },
                markers: { size: 4, colors: ['#fff'], strokeColors: color, strokeWidth: 2, hover: { size: 6 } }
            };
            charts[elementId] = new ApexCharts(document.querySelector("#" + elementId), options);
            charts[elementId].render();
        }

        // INIT
        document.addEventListener('DOMContentLoaded', () => {
            // Simulamos el inicio procesando nuestra data de prueba
            updateDashboard(mockData);
        });

    </script>
</body>
</html>
