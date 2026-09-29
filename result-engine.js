/**
 * ShopInsight AI - Result Engine
 * 담당: 결과 출력단
 * 원칙: 숫자는 코드가 계산하고, LLM은 계산된 결과만 해석한다.
 */

export const safeDivide = (numerator, denominator) =>
  denominator > 0 ? numerator / denominator : null;

export const percentChange = (current, previous) =>
  previous > 0 ? ((current - previous) / previous) * 100 : null;

export function calculateKPIs(rows) {
  const sum = (key) => rows.reduce((total, row) => total + (Number(row[key]) || 0), 0);

  const adSpend = sum("ad_spend");
  const impressions = sum("impressions");
  const clicks = sum("clicks");
  const visits = sum("visits");
  const addToCart = sum("add_to_cart");
  const purchases = sum("purchases");
  const revenue = sum("revenue");

  return {
    ad_spend: adSpend,
    impressions,
    clicks,
    visits,
    add_to_cart: addToCart,
    purchases,
    revenue,

    // 비율은 내부적으로 소수(0.032 = 3.2%)로 통일
    ctr: safeDivide(clicks, impressions),
    cvr: safeDivide(purchases, visits),
    cart_rate: safeDivide(addToCart, visits),
    cart_to_purchase_rate: safeDivide(purchases, addToCart),
    roas: safeDivide(revenue, adSpend),

    // 금액 지표
    cpc: safeDivide(adSpend, clicks),
    cpa: safeDivide(adSpend, purchases),
    aov: safeDivide(revenue, purchases),
    revenue_per_visit: safeDivide(revenue, visits),
  };
}

export function groupBy(rows, key) {
  return rows.reduce((groups, row) => {
    const value = row[key] || "unknown";
    (groups[value] ??= []).push(row);
    return groups;
  }, {});
}

export function calculatePeriodComparison(rows) {
  const monthGroups = rows.reduce((groups, row) => {
    const month = String(row.date || "").slice(0, 7);
    if (month) (groups[month] ??= []).push(row);
    return groups;
  }, {});

  const periods = Object.keys(monthGroups).sort();
  const currentPeriod = periods.at(-1) || null;
  const previousPeriod = periods.at(-2) || null;

  const current = currentPeriod ? calculateKPIs(monthGroups[currentPeriod]) : null;
  const previous = previousPeriod ? calculateKPIs(monthGroups[previousPeriod]) : null;

  const changes = {};
  if (current && previous) {
    for (const key of ["revenue", "ad_spend", "visits", "purchases", "roas", "cvr", "cpa", "aov"]) {
      changes[key] = percentChange(current[key], previous[key]);
    }
  }

  return { currentPeriod, previousPeriod, current, previous, changes };
}

export function calculateBreakdown(rows, dimension) {
  return Object.entries(groupBy(rows, dimension))
    .map(([name, groupRows]) => ({ name, ...calculateKPIs(groupRows) }))
    .sort((a, b) => b.revenue - a.revenue);
}

export function buildAnalysisPayload(rows) {
  const comparison = calculatePeriodComparison(rows);
  const currentRows = comparison.currentPeriod
    ? rows.filter((row) => String(row.date).startsWith(comparison.currentPeriod))
    : rows;

  return {
    schema_version: "1.0",
    generated_from: "deterministic_kpi_engine",
    comparison,
    breakdowns: {
      channel: calculateBreakdown(currentRows, "channel"),
      product: calculateBreakdown(currentRows, "product"),
    },
    instructions: {
      arithmetic_source: "Use only the supplied KPI values. Do not recalculate them.",
      uncertainty: "Separate observed facts from hypotheses. Do not claim causality from correlation.",
    },
  };
}
