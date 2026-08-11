# Week 2 Internship Task

## Think Step-by-Step — Chain-of-Thought & Persona Prompting

**Internship:** Neurofive Solutions
**Task:** Chain-of-Thought & Persona Prompting
**Student:** Danyal Arshad

---

## 1. Problem Statement

A small online store has a monthly marketing budget of **$10,000**.

| Campaign   |   Cost | Expected Profit |
| ---------- | -----: | --------------: |
| Campaign A | $4,000 |          $6,000 |
| Campaign B | $3,000 |          $5,000 |
| Campaign C | $5,000 |          $7,000 |

The store can choose any combination of campaigns as long as the total cost does not exceed $10,000.

**Question:** Which combination of campaigns should the store choose to maximize expected profit?

### Correct Answer

The optimal combination is **Campaign A + Campaign C**.

* Total Cost = $4,000 + $5,000 = **$9,000**
* Expected Profit = $6,000 + $7,000 = **$13,000**

Therefore, **A + C** provides the highest expected profit while staying within the budget.

---

# 2. Experiment 1 — Plain Prompt

### Prompt

```text
A small online store has a monthly marketing budget of $10,000.

Campaign A costs $4,000 and is expected to generate $6,000 in profit.

Campaign B costs $3,000 and is expected to generate $5,000 in profit.

Campaign C costs $5,000 and is expected to generate $7,000 in profit.

The store can choose any combination of campaigns as long as the total cost does not exceed $10,000.

Which combination of campaigns should the store choose to maximize expected profit?
```

### Actual AI Response

The store should choose **Campaign A and Campaign C** to maximize its expected profit at **$13,000**.

| Combination | Total Cost | Total Expected Profit | Budget Status (≤ $10,000) |
| --- | --- | --- | --- |
| Campaign A | $4,000 | $6,000 | Valid |
| Campaign B | $3,000 | $5,000 | Valid |
| Campaign C | $5,000 | $7,000 | Valid |
| Campaigns A & B | $7,000 | $11,000 | Valid |
| **Campaigns A & C** | **$9,000** | **$13,000** | **Optimal** |
| Campaigns B & C | $8,000 | $12,000 | Valid |
| Campaigns A, B & C | $12,000 | $18,000 | Exceeds Budget |

* **Optimal Choice:** **Campaign A + Campaign C**
* **Total Cost:** $9,000 (leaves $1,000 unused budget)
* **Maximum Profit:** **$13,000**
---

# 3. Experiment 2 — Persona + Step-by-Step Prompt

### Prompt

```text
You are a senior business analyst with expertise in marketing ROI and budget optimization.

A small online store has a monthly marketing budget of $10,000.

Campaign A costs $4,000 and is expected to generate $6,000 in profit.

Campaign B costs $3,000 and is expected to generate $5,000 in profit.

Campaign C costs $5,000 and is expected to generate $7,000 in profit.

The store can choose any combination of campaigns as long as the total cost does not exceed $10,000.

Think step-by-step before answering.

First, identify the valid campaign combinations within the budget. Then compare their expected profits. Finally, provide the best recommendation with a brief explanation.
```

### Actual AI Response

**Step 1: Identify Valid Combinations Within Budget**

Evaluating all single, double, and triple campaign options against the $10,000 monthly limit:

| Campaign Combination | Calculation | Total Cost | Budget Status (≤ $10,000) |
| --- | --- | --- | --- |
| **Campaign A** | $4,000 | $4,000 | Valid |
| **Campaign B** | $3,000 | $3,000 | Valid |
| **Campaign C** | $5,000 | $5,000 | Valid |
| **Campaigns A + B** | $4,000 + $3,000 | $7,000 | Valid |
| **Campaigns A + C** | $4,000 + $5,000 | $9,000 | Valid |
| **Campaigns B + C** | $3,000 + $5,000 | $8,000 | Valid |
| **Campaigns A + B + C** | $4,000 + $3,000 + $5,000 | $12,000 | Exceeds Budget (Invalid) |

---

**Step 2: Compare Expected Profits**

Comparing expected total profits across all feasible options:

1. **Campaigns A + C:** $6,000 + $7,000 = **$13,000 profit** (Cost: $9,000)
2. **Campaigns B + C:** $5,000 + $7,000 = **$12,000 profit** (Cost: $8,000)
3. **Campaigns A + B:** $6,000 + $5,000 = **$11,000 profit** (Cost: $7,000)
4. **Campaign C (Single):** **$7,000 profit** (Cost: $5,000)
5. **Campaign A (Single):** **$6,000 profit** (Cost: $4,000)
6. **Campaign B (Single):** **$5,000 profit** (Cost: $3,000)

---

**Step 3: Business Recommendation**

Select **Campaign A and Campaign C**.

* **Maximum Net Yield:** This pairing delivers **$13,000** in expected profit, exceeding the next best option (B + C) by $1,000.
* **Budget Utilization:** The combined cost is **$9,000**, leaving an unallocated buffer of $1,000 in your monthly budget.
* **Strategic ROI Note:** While Campaign B offers the highest individual Return on Investment (166.7% vs. A's 150% and C's 140%), running A + C deploys more of your available budget into profitable channels, resulting in a higher total dollar return.

---

# 4. Before vs After Comparison

| Criteria                 | Plain Prompt        | Persona + Step-by-Step            |
| ------------------------ | ------------------- | --------------------------------- |
| **Correctness**          | ✅ Correct           | ✅ Correct                         |
| **Clarity**              | Short and direct    | More structured                   |
| **Reasoning/Analysis**   | Limited explanation | Clear comparison of options       |
| **Domain Context**       | No specific role    | Senior Business Analyst persona   |
| **Final Recommendation** | A + C               | A + C with stronger justification |

---

# 5. Analysis

Both prompts produced the **same correct answer**, because the problem is relatively simple and the required calculations are straightforward.

However, the Persona + Step-by-Step prompt produced a more structured analysis by giving the model a specific professional role and explicitly asking it to compare the possible options before making a recommendation.

The **persona** provides domain context and encourages a business-oriented response, while the **step-by-step instruction** encourages a systematic analysis of the available choices.

This experiment also showed that these techniques do not automatically improve accuracy on every problem. Their main benefit can be improved **structure, clarity, and consistency**, especially when the problem becomes more complex.

---

# 6. Key Learning

From this experiment, I learned that prompt engineering can influence not only **what** an AI answers, but also **how it approaches and presents a problem**.

A simple prompt may be sufficient for straightforward questions, while adding a relevant persona and structured reasoning instructions can make responses more organized and useful for complex tasks.

---
