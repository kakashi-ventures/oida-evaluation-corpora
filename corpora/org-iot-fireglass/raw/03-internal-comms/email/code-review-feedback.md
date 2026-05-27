# Email: Re: PR #47 — CASL rules refactor

**From:** Samir Osei <samir.osei@atlasforge.dev>
**To:** Clara Duval <clara.duval@atlasforge.dev>
**CC:**
**Date:** 2025-10-01 15:18
**Subject:** Re: PR #47 — CASL rules refactor

---

Clara,

I reviewed your PR. The TypeScript types for the permission matrix are excellent — that's going to save us a lot of headaches later. Well done.

A few concerns:

**1. CASL ability definitions need tighter scope**

Currently, Technicians can see all inspections across all installations:

```
ability('read', 'inspection')
```

This should be scoped to installations they're assigned to. We need something like:

```
ability('read', 'inspection', { installation_id: { $in: userAssignedInstallations } })
```

This gets us back to the field later. Field technicians should not see Milan site data if they're assigned only to the Rome site.

**2. The usePermissions hook is re-evaluating on every render**

Right now it's calling `ability.can()` on every component render, which re-runs the entire permission check logic. It's not expensive, but it's wasteful. Add a useMemo wrapper around the ability check so we only recompute if the ability object or the action changes.

**3. Permission logic should move to middleware**

Instead of checking permissions in individual components, push that to the API layer via middleware. Components ask "can I do X?" and get a boolean; the backend enforces it on mutations. This separation keeps the presentation layer thin and shifts the trust to the server (where it belongs).

Great work overall. Once you address these, it's ready to merge.

— Samir

---

**From:** Clara Duval <clara.duval@atlasforge.dev>
**Date:** 2025-10-01 16:42
**Subject:** Re: PR #47 — CASL rules refactor

Thanks, Samir! I'll add the installation scope and move the permission checks to middleware. The middleware approach makes sense — keeps the API as the source of truth.

On the memoization point: React 18 handles a lot of this better than you think with automatic batching. The re-renders are cheap because the ability object itself is stable (useContext). But I'll add the useMemo anyway — doesn't hurt and makes the intent clear.

Pushing v2 tomorrow.

— Clara
