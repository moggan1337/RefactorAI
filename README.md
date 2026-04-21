# RefactorAI - AI-Powered Technical Debt Analyzer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/AI-Analysis-FF6B6B.svg" alt="AI">
</p>

> **Quantify your technical debt. Prioritize your refactoring. Ship faster.**

RefactorAI uses machine learning and static analysis to identify, measure, and prioritize technical debt across your entire codebase.

## 🎬 Demo

![RefactorAI Demo](demo.gif)

*AI-powered technical debt analysis and refactoring recommendations*

## ✨ Features

- **AI-Powered Analysis** - GPT-4 powered code review and suggestions
- **Debt Quantification** - Convert debt into estimated hours/dollars
- **Smart Prioritization** - AI ranks fixes by impact vs effort
- **Trend Tracking** - Monitor debt over time with dashboards
- **Automated Fixes** - One-click refactoring for common patterns

## 🚀 Quick Start

```bash
pip install refactorai
refactorai analyze ./src
refactorai dashboard
```

## 📊 Technical Debt Report Demo

### Executive Summary

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    TECHNICAL DEBT ANALYSIS REPORT                                │
│                    ════════════════════════════════                              │
│                    Generated: 2024-04-21 14:30:00                                │
│                    Repository: moggan1337/platform-api                          │
│                    Branch: main | Commit: a1b2c3d                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  📊 EXECUTIVE SUMMARY                                                           │
│  ───────────────────                                                            │
│                                                                                  │
│  Technical Debt Score    ██████████████████░░░░░░░░░░░  67/100 (Moderate)       │
│  Debt Trend              📈 +2.3% this sprint (↑ Bad)                          │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                               │ │
│  │   Total Debt Items:     247        Total Estimated Hours:    456           │ │
│  │   Critical Issues:       12        Cost to Fix All:          $45,600        │ │
│  │   High Priority:         34        Velocity Impact:         -15%           │ │
│  │   Medium Priority:        89        Bug Risk Factor:         2.4x           │ │
│  │   Low Priority:          112        Maintainability:         Fair           │ │
│  │                                                                               │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Debt Breakdown by Category

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DEBT BREAKDOWN BY CATEGORY                              │
└─────────────────────────────────────────────────────────────────────────────────┘

  COMPLEXITY DEBT                          CODE DUPLICATION                        
  ████████████████████░░░░░░░░░  28%       ████████████████░░░░░░░░░  18%          
  Est: 128 hours                          Est: 82 hours                           
  Impact: High                            Impact: Medium                           
                                                                                  
  LEGACY PATTERNS                          PERFORMANCE ISSUES                     
  ████████████████░░░░░░░░░░░░  22%       ████████████░░░░░░░░░░░░░  15%          
  Est: 100 hours                          Est: 68 hours                           
  Impact: High                            Impact: High                            
                                                                                  
  DEPENDENCY DEBT                          SECURITY VULNERABILITIES                
  ████████░░░░░░░░░░░░░░░░░░░  10%       ████░░░░░░░░░░░░░░░░░░░░  5%           
  Est: 45 hours                           Est: 23 hours                           
  Impact: Medium                          Impact: Critical ⚠️                     
                                                                                  
  OTHER                                    TEST COVERAGE GAPS                      
  ███░░░░░░░░░░░░░░░░░░░░░░░░  2%        ████████████░░░░░░░░░░░░░  0%           
  Est: 10 hours                           Est: 0 hours (covered separately)      

  Total: 456 hours                        Total: $45,600 (at $100/hr)             
```

### Critical Issues Detail

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         🚨 CRITICAL ISSUES (12)                                  │
│                         Require immediate attention!                            │
└─────────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 🔴 CRITICAL #1: Authentication Bypass in /api/auth                          │
  │ ─────────────────────────────────────────────────────                       │
  │ File: src/api/auth/login.py:45                                              │
  │ Severity: CRITICAL | Impact: Security | Effort: 2h                         │
  │                                                                             │
  │ AI Analysis:                                                                │
  │ The authentication check was commented out for "testing" and never          │
  │ restored. This allows unauthenticated access to protected endpoints.       │
  │                                                                             │
  │ Current Code:                                                               │
  │ ┌───────────────────────────────────────────┐                               │
  │ │  def get_user_data(request):              │                               │
  │ │    # TODO: add auth check later           │ ←── DISABLED!                 │
  │ │    # if not request.user:                │                               │
  │ │    #     return unauthorized()            │                               │
  │ │    return get_data(request.user.id)       │                               │
  │ └───────────────────────────────────────────┘                               │
  │                                                                             │
  │ AI Recommendation:                                                          │
  │ Immediately restore authentication check. This is a critical               │
  │ security vulnerability that could lead to data exposure.                    │
  │                                                                             │
  │ Suggested Fix:                                                             │
  │ ┌───────────────────────────────────────────┐                               │
  │ │  def get_user_data(request):              │                               │
  │ │    if not request.user:                   │                               │
  │ │        raise UnauthorizedError()          │                               │
  │ │    return get_data(request.user.id)       │                               │
  │ └───────────────────────────────────────────┘                               │
  │                                                                             │
  │ Confidence: 98% | Fix available: YES (one-click)                           │
  └─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 🔴 CRITICAL #2: N+1 Query Problem in Reports Module                         │
  │ ─────────────────────────────────────────────────────                       │
  │ File: src/services/reports.py:89                                            │
  │ Severity: HIGH | Impact: Performance | Effort: 4h                           │
  │                                                                             │
  │ AI Analysis:                                                                │
  │ The report generation queries the database once per item in a loop.         │
  │ With 10,000 items, this creates 10,000 database roundtrips.                 │
  │                                                                             │
  │ Current (Inefficient):                                                      │
  │ ┌───────────────────────────────────────────┐                               │
  │ │  for order in orders:                     │                               │
  │ │      user = db.query(User).get(order.id)  │ ←── 10,000 queries!           │
  │ │      items.append({order, user})          │                               │
  └───────────────────────────────────────────┘                               │
  │                                                                             │
  │ AI Recommendation:                                                          │
  │ Use eager loading or batch queries to reduce database calls.                │
  │                                                                             │
  │ Suggested Fix:                                                             │
  │ ┌───────────────────────────────────────────┐                               │
  │ │  # Eager load users in single query                              │         │
  │ │  orders = db.query(Order).options(                               │         │
  │ │      joinedload(Order.user)                                       │         │
  │ │  ).all()                                                          │         │
  │ │  # Now access order.user without additional queries               │         │
  └───────────────────────────────────────────┘                               │
  │                                                                             │
  │ Expected Improvement: 94% faster (15s → 0.9s) | Confidence: 95%            │
  └─────────────────────────────────────────────────────────────────────────────┘
```

### AI Refactoring Suggestions

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         🤖 AI REFACTORING RECOMMENDATIONS                        │
│                         Generated by GPT-4 Code Analysis                        │
└─────────────────────────────────────────────────────────────────────────────────┘

  HIGH IMPACT REFACTORINGS (Do First)
  ════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 💡 REFACTOR #1: Extract Service Layer                                       │
  │ ─────────────────────────────────────────────────                          │
  │                                                                             │
  │ Problem: Business logic is scattered across 47 different controller files   │
  │                                                                             │
  │ Impact:  ████████████████████████░░░░  85% code quality improvement        │
  │ Effort:  ██████████░░░░░░░░░░░░░░░░░  40 hours                            │
  │ Risk:    ███░░░░░░░░░░░░░░░░░░░░░░░░░  Low (automated)                     │
  │                                                                             │
  │ AI Suggested Architecture:                                                 │
  │ ┌───────────────────────────────────────────────────────────────────────┐   │
  │ │  src/                                                                  │   │
  │ │  ├── controllers/     # HTTP handling only                            │   │
  │ │  ├── services/        # Business logic (extract here)                 │   │
  │ │  │   ├── order_service.py    # 12,000 lines → 400 lines              │   │
  │ │  │   ├── user_service.py     # 8,500 lines → 350 lines              │   │
  │ │   │   └── payment_service.py # 6,200 lines → 280 lines              │   │
  │ │   └── repositories/   # Data access                                   │   │
  │ └───────────────────────────────────────────────────────────────────────┘   │
  │                                                                             │
  │ ROI: Payback in 3 sprints (velocity improvement)                           │
  └─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 💡 REFACTOR #2: Replace Callback Hell with Async/Await                      │
  │ ─────────────────────────────────────────────────                          │
  │                                                                             │
  │ Problem: 12 files with callback chains 5+ levels deep                       │
  │                                                                             │
  │ Impact:  █████████████████░░░░░░░░░░  60% maintainability improvement      │
  │ Effort:  ████████░░░░░░░░░░░░░░░░░░  24 hours                             │
  │ Risk:    ██████░░░░░░░░░░░░░░░░░░░░  Medium (requires testing)             │
  │                                                                             │
  │ Example Transformation:                                                     │
  │ ┌───────────────────────────────────────────────────────────────────────┐   │
  │ │  BEFORE (callback hell):           AFTER (async/await):              │   │
  │ │  ───────────────────────          ─────────────────────              │   │
  │ │                                    async def process_order(id):     │   │
  │ │  getUser(id, (err, user) => {      try:                               │   │
  │ │    getOrders(user.id, (err, ord)   │   user = await get_user(id)      │   │
  │ │      => {                          │   orders = await get_orders(    │   │
  │ │        getItems(ord.id, (err,      │       user.id                    │   │
  │ │          items => {                │   )                               │   │
  │ │            // ... 5 more levels   │   items = await get_items(       │   │
  │ │          })                        │       orders.id                  │   │
  │ │      })                            │   )                               │   │
  │ │  })                                │   return format_response(         │   │
  │ │                                    │       user, orders, items         │   │
  │ │                                    │   )                               │   │
  │ │                                    │ except Error as e:               │   │
  │ │                                    │   logger.error(e)                │   │
  │ │                                    │   raise ProcessingError()        │   │
  │ └───────────────────────────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 💡 REFACTOR #3: Implement Repository Pattern                                 │
  │ ─────────────────────────────────────────────────                          │
  │                                                                             │
  │ Problem: Direct SQL queries scattered across 89 files                       │
  │                                                                             │
  │ Impact:  ████████████████░░░░░░░░░░░  45% testability improvement          │
  │ Effort:  ████████████████████░░░░░░░  56 hours                             │
  │ Risk:    ██░░░░░░░░░░░░░░░░░░░░░░░░░  Very Low (can automate)              │
  │                                                                             │
  │ This will make your code:                                                   │
  │ ✓ Testable without database                                                 │
  │ ✓ Portable across databases                                                │
  │ ✓ Easier to understand and maintain                                        │
  └─────────────────────────────────────────────────────────────────────────────┘
```

### Technical Debt Over Time

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         TECHNICAL DEBT TREND                                     │
│                         Last 12 Sprints                                          │
└─────────────────────────────────────────────────────────────────────────────────┘

  Score                                                                           
  100 ┤                                                                  ████     
   90 ┤                                                           ████████░░░  
   80 ┤                                                     ████████████░░░░░  
   70 ┤                                              ████████████████░░░░░░░  
   60 ┤                                       ██████████████████████░░░░░░░  
   50 ┤                                ██████████████████████████████████░░░  
   40 ┤                         ████████████████████████████████████████████    
   30 ┤                  ████████████████████████████████████████████████      
   20 ┤           ████████████████████████████████████████████████████████      
   10 ┤    ████████████████████████████████████████████████████████████████      
      ┼────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────           
       S1   S2   S3   S4   S5   S6   S7   S8   S9   S10  S11  S12            
                                                                              
      █ = Debt introduced    ░ = Debt paid down                               
                                                                              
  Summary:                                                                   
  ┌─────────────────────────────────────────────────────────────────────────┐  
  │  Started Sprint 1:     34 hours of debt                                  │  
  │  Debt Introduced:      312 hours                                         │  
  │  Debt Paid Down:       178 hours                                         │  
  │  Current Sprint:       168 hours                                         │  
  │                                                                          │  
  │  📈 Trend: -8% per sprint (on track!)                                   │  
  │  🎯 Target: < 50 hours by Q4                                             │  
  └─────────────────────────────────────────────────────────────────────────┘
```

## 🛠️ Installation

```bash
pip install refactorai
```

## 📖 Usage

```bash
# Analyze codebase
refactorai analyze ./src

# Interactive dashboard
refactorai dashboard

# Generate report
refactorai report --format html --output ./reports/

# Track progress
refactorai track --sprint 12

# Auto-fix common issues
refactorai fix --auto --dry-run
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT © 2024 moggan1337
