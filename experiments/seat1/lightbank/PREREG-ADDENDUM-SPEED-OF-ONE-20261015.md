# Pre-implementation ADDENDUM C1 — The Law of Space, Light, Colour and Speed of One

Added **before executable implementation** to the existing preregistration commit 7355b60363954a1128d96e46614bae4dbdb2373b.

Primary original source: https://github.com/JesseBrown1980/the-law-of-space-and-light-and-color-and-travel-at-the-speed-of-one/blob/main/README.md — Git blob `6412cb3b82ec084b03b68c9c4d074a58920ac1ee`. GitHub Pages: https://jessebrown1980.github.io/the-law-of-space-and-light-and-color-and-travel-at-the-speed-of-one/ . Browser depiction is an explanatory animation, not optical storage instrumentation.

The test's exact algebra:
- Define integer matrix `M=3I-J` for the 3-lane colour vector, with 2 on diagonal and -1 off diagonal. Exact integer assertions `M*M=3*M`, `M*[1,1,1]=0`, `sum(M*x)=0`. This encodes the source's rational projector `P=I-J/3`; it is idempotent `P^2=P`, rank 2 and removes a common centre mode. Distinguish the -1/3 off-diagonal and +2/3 diagonal from any physical propagation speed.
- For deterministic 27 source vectors `x=[w%3,(w//3)%3,(w//9)%3]`, compute `y=M*x` and ground `g=sum(x)`, exact reconstruct `x_i=(y_i+g)/3`. Verify modulo 3 exactness. The common-mode-shift negative control `M*(x+[5,5,5])=M*x` shows **projector output alone cannot store/recover the complete original memory**. This illustrates the August claim 'history sits in the ground', while exposing the need to store the common-mode metadata separately.
- Projector "instant" is an **algebraic identity only**: two calculated values can be constrained without a transmitted signal. All digital colour-bank data transfers and delayed-feedback decisions occur in explicit ordered compute ticks. Any nonzero time-of-flight, photonic hardware retention, or speed-of-light claim requires measured apparatus and is **out of scope**.
- Correct physics limitation: a photon has no inertial rest frame; zero null interval does not imply a physical photon-owned coordinate frame or infinite-speed communication. Source philosophical interpretation is neither verified nor refuted by the projector identity.

Additional preregistered **falsifiers**, run separately from packet/kinetic test and recorded in its evidence:
1. One-hot optical census T/A/R 9/9/9 across 27 wave addresses; `T+A+R=1` exactly for each virtual classification. These are *counts*, NOT photon interaction outcomes.
2. The integer projector, common mode, reassembly and negative collision tests all executed for 27 vectors, reporting `projector_exact=27`, `ground_reconstruction=27`, `common_mode_loss_detected=27`. Require any intentionally omitted ground component to be classified **NONINVERTIBLE**, not a successful memory read.

This supplement does not change the pre-registered 109,350 FRAME, 10,935 MEMORY row contract, 2,100-byte chunking, pulse schedule, corruption protocol, cross-runtime checks or Release/Consent gate.
