# TODO

## Duality gap and intercepts

- [ ] Reframe the feasible-dual-point discussion around conditionally refitting
  the intercept and then scaling the generalized residual. Cite Koh, Kim, and
  Boyd (2007) for this construction, and present the domain-preserving anchor
  interpolation as the numerical and degenerate-case fallback used by the
  implementation.
- [ ] Add the published context for intercept-aware duality: cite El Ghaoui,
  Viallon, and Rabbani (2012) for Gaussian centering, Ndiaye, Fercoq, Gramfort,
  and Salmon (2017) for the general Gap Safe framework and its intercept
  remark, and Massias, Vaiter, Gramfort, and Salmon (2020) for residual scaling
  and tighter dual candidates.
- [ ] State when an unpenalized intercept has no finite minimizer, including
  single-class binomial responses, all-zero Poisson responses, and absent
  multinomial classes. Explain that a feasible dual certificate may still
  exist even when the primal infimum is not attained at a finite intercept.
- [ ] Qualify the safe-screening discussion by its curvature assumptions. In
  particular, distinguish validity of the canonical Poisson duality gap from
  validity of a classical Gap Safe sphere, and cite the local-strong-concavity
  framework of Dantas, Soubies, and Févotte (2021).
