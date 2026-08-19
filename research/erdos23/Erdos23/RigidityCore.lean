import Erdos23.AnalyticCore

namespace Erdos23

/-- Adjacency in the five-cycle, written on `ZMod 5`. -/
def c5Adjacent (i j : ZMod 5) : Prop :=
  j = i + 1 ∨ i = j + 1

/-- The two neighbours of a vertex in the five-cycle. -/
def c5NeighborSet (i : ZMod 5) : Finset (ZMod 5) :=
  {i - 1, i + 1}

/-- Every independent pair of vertices in `C₅` is the neighbour set of a unique vertex. -/
theorem c5_independent_pair_classification :
    ∀ S : Finset (ZMod 5),
      S.card = 2 →
      (∀ a ∈ S, ∀ b ∈ S, a ≠ b → ¬ c5Adjacent a b) →
      ∃! i : ZMod 5, S = c5NeighborSet i := by
  native_decide

/-- Two `C₅` neighbour sets are disjoint exactly when their class vertices are adjacent. -/
theorem c5_neighbor_sets_disjoint_iff_adjacent :
    ∀ i j : ZMod 5,
      Disjoint (c5NeighborSet i) (c5NeighborSet j) ↔ c5Adjacent i j := by
  native_decide

/-- The tangent line to `1 / d` at `d = 2 / 5`. -/
theorem reciprocal_tangent (d : ℝ) (hd : 0 < d) :
    5 - 25 * d / 4 ≤ 1 / d := by
  apply (le_div_iff₀ hd).2
  nlinarith [sq_nonneg (5 * d - 2)]

private theorem reciprocal_tangent_eq_forces (d : ℝ) (hd : 0 < d)
    (h : 5 - 25 * d / 4 = 1 / d) : d = 2 / 5 := by
  have h' : (1 : ℝ) = (5 - 25 * d / 4) * d := by
    exact (div_eq_iff hd.ne').1 h.symm
  nlinarith [sq_nonneg (5 * d - 2)]

/-- Equality in the five-term reciprocal bound forces all five weighted degrees to be `2 / 5`. -/
theorem five_reciprocal_equality_rigidity
    (d₀ d₁ d₂ d₃ d₄ : ℝ)
    (h₀ : 0 < d₀) (h₁ : 0 < d₁) (h₂ : 0 < d₂) (h₃ : 0 < d₃) (h₄ : 0 < d₄)
    (hsum : d₀ + d₁ + d₂ + d₃ + d₄ = 2)
    (hrecip : 1 / d₀ + 1 / d₁ + 1 / d₂ + 1 / d₃ + 1 / d₄ = 25 / 2) :
    d₀ = 2 / 5 ∧ d₁ = 2 / 5 ∧ d₂ = 2 / 5 ∧ d₃ = 2 / 5 ∧ d₄ = 2 / 5 := by
  have ht₀ := reciprocal_tangent d₀ h₀
  have ht₁ := reciprocal_tangent d₁ h₁
  have ht₂ := reciprocal_tangent d₂ h₂
  have ht₃ := reciprocal_tangent d₃ h₃
  have ht₄ := reciprocal_tangent d₄ h₄
  have hlower :
      (5 - 25 * d₀ / 4) + (5 - 25 * d₁ / 4) + (5 - 25 * d₂ / 4) +
          (5 - 25 * d₃ / 4) + (5 - 25 * d₄ / 4) = 25 / 2 := by
    nlinarith
  have heq₀ : 5 - 25 * d₀ / 4 = 1 / d₀ := by nlinarith
  have heq₁ : 5 - 25 * d₁ / 4 = 1 / d₁ := by nlinarith
  have heq₂ : 5 - 25 * d₂ / 4 = 1 / d₂ := by nlinarith
  have heq₃ : 5 - 25 * d₃ / 4 = 1 / d₃ := by nlinarith
  have heq₄ : 5 - 25 * d₄ / 4 = 1 / d₄ := by nlinarith
  exact ⟨reciprocal_tangent_eq_forces d₀ h₀ heq₀,
    reciprocal_tangent_eq_forces d₁ h₁ heq₁,
    reciprocal_tangent_eq_forces d₂ h₂ heq₂,
    reciprocal_tangent_eq_forces d₃ h₃ heq₃,
    reciprocal_tangent_eq_forces d₄ h₄ heq₄⟩

/-- The five class-mass equations forced by sharpness have the unique balanced solution. -/
theorem balanced_five_class_masses
    (a₀ a₁ a₂ a₃ a₄ : ℝ)
    (h₀ : a₄ + a₁ = 2 / 5)
    (h₁ : a₀ + a₂ = 2 / 5)
    (h₂ : a₁ + a₃ = 2 / 5)
    (h₃ : a₂ + a₄ = 2 / 5)
    (h₄ : a₃ + a₀ = 2 / 5) :
    a₀ = 1 / 5 ∧ a₁ = 1 / 5 ∧ a₂ = 1 / 5 ∧ a₃ = 1 / 5 ∧ a₄ = 1 / 5 := by
  constructor
  · linarith
  constructor
  · linarith
  constructor
  · linarith
  constructor <;> linarith

/-- If the sharp bound is attained, the intermediate reciprocal parameter is exactly `25 / 2`. -/
theorem sharp_cost_forces_gamma (Λ γ : ℝ)
    (hΛ : Λ = 1 / 25)
    (hγ : 25 / 2 ≤ γ)
    (hcost : Λ ≤ 1 / (2 * γ)) :
    γ = 25 / 2 := by
  have hγpos : 0 < 2 * γ := by nlinarith
  rw [hΛ] at hcost
  have hcross := (le_div_iff₀ hγpos).1 hcost
  nlinarith

/-- The reciprocal-cycle lower bound can be sharp only at cycle length five. -/
theorem sharp_reciprocal_cycle_length (L : ℝ)
    (hL : 5 ≤ L)
    (hsharp : 2 * L ^ 2 / (L - 1) ≤ 25 / 2) :
    L = 5 := by
  have hden : 0 < L - 1 := by linarith
  have hcross := (div_le_iff₀ hden).1 hsharp
  have hnonneg : 0 ≤ (L - 5) * (4 * L - 5) := by positivity
  nlinarith

end Erdos23
