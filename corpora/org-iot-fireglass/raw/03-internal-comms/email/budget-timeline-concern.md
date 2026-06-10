# Email: Heads up — timeline pressure

**From:** Samir Osei <samir.osei@atlasforge.dev>
**To:** Clara Duval <clara.duval@atlasforge.dev>
**CC:** John Smith <john.smith@atlasforge.dev>
**Date:** 2025-09-22 10:05
**Subject:** Heads up — timeline pressure

---

Clara, John,

I want to be transparent: Alberto mentioned in a call last week that he's feeling timeline pressure. We were supposed to hit MVP by end of October. The Helion firmware unknowns and the connection reliability issues we found in Milan cost us about 2 sprints of rework and blockers.

We're at week 8. We have 7 weeks left to launch. It's tight.

Here's my plan to get back on track:

**Deferring to Phase 2 (post-launch):**
- Offline sync for sensor readings (we're keeping it for forms, which works)
- Advanced reporting (PDF export with charts, trend analysis)
- Mobile app

**Keeping in MVP:**
- Core CRUD for installations/windows
- Real-time sensor ingestion with retry logic
- User/role management and audit logs
- Basic inspection forms
- Authentication and access control

**What I need from you:**
- Clara: Focus on permission layer and inspection forms. The auth we built is solid; let's not refactor it. TypeScript types are your friend.
- John: Continue field validation. One more round of testing on the connectivity issue, then we pull back to 1 day/week for the final push.

The good news: the core architecture is sound. We're not rewriting anything fundamental. We're just being ruthless about scope.

Let's ship the MVP and iterate.

— Samir
