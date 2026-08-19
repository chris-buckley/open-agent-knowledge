import Mathlib

namespace Erdos23

/-- The edge weight used by the fractional odd-cycle cover construction. -/
def coverWeight {V E : Type*} (q : V → ℝ) (γ : ℝ)
    (left right : E → V) (e : E) : ℝ :=
  (q (left e) + q (right e)) / (2 * γ)

/-- The constructed edge weights are nonnegative. -/
theorem coverWeight_nonneg {V E : Type*} (q : V → ℝ) (γ : ℝ)
    (left right : E → V) (hq : ∀ v, 0 ≤ q v) (hγ : 0 < γ) (e : E) :
    0 ≤ coverWeight q γ left right e := by
  unfold coverWeight
  positivity

/-- If every odd cycle has endpoint charge at least `2 * γ`, the construction covers it. -/
theorem coverWeight_feasible {V E C : Type*} [DecidableEq E]
    (cycle : C → Finset E) (q : V → ℝ) (γ : ℝ)
    (left right : E → V) (hγ : 0 < γ)
    (hcycle : ∀ c, 2 * γ ≤ ∑ e ∈ cycle c, (q (left e) + q (right e))) :
    ∀ c, 1 ≤ ∑ e ∈ cycle c, coverWeight q γ left right e := by
  intro c
  simp only [coverWeight]
  rw [← Finset.sum_div]
  exact (le_div_iff₀ (by positivity)).2 (hcycle c)

/-- The objective value telescopes once the endpoint-charge identity is known. -/
theorem coverWeight_cost {V E : Type*} [Fintype E]
    (q : V → ℝ) (γ : ℝ) (left right : E → V) (w : E → ℝ)
    (hcost : ∑ e, w e * (q (left e) + q (right e)) = 1) :
    ∑ e, w e * coverWeight q γ left right e = 1 / (2 * γ) := by
  simp only [coverWeight]
  calc
    (∑ e, w e * ((q (left e) + q (right e)) / (2 * γ))) =
        ∑ e, (w e * (q (left e) + q (right e))) / (2 * γ) := by
          apply Finset.sum_congr rfl
          intro e he
          simpa only [mul_div_assoc]
    _ = (∑ e, w e * (q (left e) + q (right e))) / (2 * γ) := by
          rw [Finset.sum_div]
    _ = 1 / (2 * γ) := by rw [hcost]

/-- The reciprocal-cycle expression is minimized at length five. -/
theorem reciprocal_constant_from_length_five (L : ℝ) (hL : 5 ≤ L) :
    (25 : ℝ) / 2 ≤ 2 * L ^ 2 / (L - 1) := by
  have hden : 0 < L - 1 := by linarith
  apply (le_div_iff₀ hden).2
  have h1 : 0 ≤ L - 5 := by linarith
  have h2 : 0 ≤ 4 * L - 5 := by linarith
  nlinarith [mul_nonneg h1 h2]

/-- A cycle charge of at least `25 / 2` gives objective at most `1 / 25`. -/
theorem cost_le_one_twenty_five (γ : ℝ) (hγ : (25 : ℝ) / 2 ≤ γ) :
    1 / (2 * γ) ≤ (1 : ℝ) / 25 := by
  have hγpos : 0 < γ := lt_of_lt_of_le (by norm_num) hγ
  apply (div_le_div_iff₀ (by positivity : 0 < 2 * γ) (by norm_num : (0 : ℝ) < 25)).2
  nlinarith

/-- The exact constant obtained from an odd-girth lower bound. -/
theorem odd_girth_cost_identity (g : ℝ) (hg : 1 < g) :
    1 / (2 * (2 * g ^ 2 / (g - 1))) = (g - 1) / (4 * g ^ 2) := by
  have hg0 : g ≠ 0 := by linarith
  have hgm1 : g - 1 ≠ 0 := by linarith
  field_simp [hg0, hgm1]
  <;> ring

/-- The odd-girth-seven constant is `3 / 98`. -/
theorem odd_girth_seven_constant :
    ((7 : ℝ) - 1) / (4 * (7 : ℝ) ^ 2) = (3 : ℝ) / 98 := by
  norm_num

/-- The odd-girth-nine constant is `2 / 81`. -/
theorem odd_girth_nine_constant :
    ((9 : ℝ) - 1) / (4 * (9 : ℝ) ^ 2) = (2 : ℝ) / 81 := by
  norm_num

/-- The complete analytic core: feasibility plus the endpoint identity implies the sharp cost. -/
theorem constructed_cover_cost_le_one_twenty_five {V E : Type*} [Fintype E]
    (q : V → ℝ) (γ : ℝ) (left right : E → V) (w : E → ℝ)
    (hcost : ∑ e, w e * (q (left e) + q (right e)) = 1)
    (hγ : (25 : ℝ) / 2 ≤ γ) :
    ∑ e, w e * coverWeight q γ left right e ≤ (1 : ℝ) / 25 := by
  rw [coverWeight_cost q γ left right w hcost]
  exact cost_le_one_twenty_five γ hγ

end Erdos23
