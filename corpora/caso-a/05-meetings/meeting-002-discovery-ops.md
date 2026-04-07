# Meeting 002: Operations Discovery
**Date:** September 22, 2025
**Location:** ClearPath Solutions Inc., Florence office, Operations Room
**Attendees:** Yuki Tanaka (Analyst, Meridian Labs), Priya Anand (Head of Operations, ClearPath), Marco Fiore (Team Lead, ClearPath), Laura Galli (Team Lead, ClearPath), Riccardo Boni (Team Lead, ClearPath), Chiara Lentini (Team Lead, ClearPath)
**Duration:** 120 minutes (14:00–16:00)

---

[14:02] Yuki: Thank you all for taking the time today. This is really helpful for us to understand the ground truth of how things work. Priya, I've read through the documentation you sent, and it's detailed, but I'm sure there are things that don't quite match reality, right?

[14:03] Priya: *laughs* You could say that. Welcome to consulting reality. Marco, why don't you walk through your team's workflow?

[14:04] Marco: Sure. So our workflow, the way it actually happens—and this is different from what's written down—is that when a client file comes in, the initial review goes to whoever's available. We don't have formal assignment. It used to be Chiara's job to do that, but then we needed her elsewhere, so now it's sort of... whoever notices it. Sometimes it sits in the intake email for a day before anyone picks it up.

[14:06] Yuki: Okay. Just to walk through this step by step—let me get really granular. When a new client request comes in, what actually happens? Marco, start from the moment you receive it. What systems is it in? How long until someone sees it?

[14:07] Marco: Usually it comes in as an email to the general inbox, sometimes directly to me. Someone—usually me, or whoever's sitting at their desk—sees it and downloads the file. We have a shared folder where we dump the compliance documents. Then we check some internal notes about the client—if we've worked with them before, what their risk profile is.

[14:08] Yuki: And this is all outside the legacy system? Or does the legacy system play a role here?

[14:09] Marco: Good question. It *should* play a role. Technically the system has a module for intake. But it's so slow and clunky that nobody really uses it. We just email and use the shared folder. The system gets updated later, if at all.

[14:11] Laura: Actually, my team's approach is a bit different. We do try to log it in the intake module, but only because I insisted. When a request comes in, it gets forwarded to me first—I'm the gatekeeper for my team—and I review the client history in the legacy system. Then I assign it to a specific consultant based on their skill and capacity. That consultant owns the entire audit through to my sign-off.

[14:13] Yuki: Okay, so Laura, you're saying you do use the legacy system as part of the intake?

[14:14] Laura: Yes, but I'm probably an outlier. Most of it sits outside the system. I just think it's cleaner to have a record of who was assigned when. Makes accountability clearer.

[14:15] Marco: That's fine if you've got the bandwidth to be a gatekeeper. My team's too busy for that layer. By the time intake gets assigned, we've already got three other audits in the queue.

[14:16] Yuki: *makes note* So intake happens manually, assignment is ad-hoc for Marco's team, structured for Laura's team. From assignment, what happens next?

[14:18] Laura: The consultant does the initial audit work—evidence gathering, compliance checks, gap identification. That usually takes 1 to 2 days for a standard audit, longer for complex ones. Then it comes back to me for review and sign-off.

[14:19] Marco: Same thing, roughly. Initial work happens, then it needs review. That's where we hit a bottleneck, honestly. The review takes time, and I'm the only one who signs off on most of these.

[14:21] Yuki: How long does the review step take? Just the review, not the initial work.

[14:22] Marco: *pauses* Maybe half a day? Sometimes a day if there are issues that need rework. But the problem is I've got other stuff too—I'm reviewing for multiple junior people, attending meetings, dealing with escalations. So a piece that's ready for review might sit for two or three days before I even get to it.

[14:24] Riccardo: *speaks up* Yeah, that's exactly what I'm seeing on the reporting side. A lot of our reporting delays are because people are waiting for Marco or Laura to review and approve their work before it even gets to me. Then I'm assembling reports from things that have been sitting in draft status for a week.

[14:25] Yuki: You're doing the report assembly, Riccardo? Walk me through that.

[14:26] Riccardo: Right. So once the audit work is reviewed and signed, it comes to me. I'm supposed to pull the data from the legacy system, do some aggregations, generate the client-facing report. But here's the thing—the legacy system's reporting module is terrible. I spend at least a day per complex report just wrestling with the system to get the numbers out. The export formats are broken half the time. So I end up doing a lot of manual work in Excel just to create something that looks professional.

[14:28] Yuki: And this is for every audit?

[14:29] Riccardo: Every single one. It's incredibly inefficient. I've asked if we can improve the system or at least streamline the export process, but it's on the backlog. Meanwhile, reports are delayed because I'm stuck doing manual reconciliation.

[14:30] Marco: See, this is what I mean about the legacy system. We thought we'd be using it for everything, but it's just gotten in the way. Riccardo's right—the reporting is where it really breaks down.

[14:32] Yuki: Okay, so let me map this. Initial intake, ad-hoc assignment, initial audit work, review bottleneck, then another bottleneck at reporting. Let me ask: from the moment a client file arrives, to the moment they get the final report—how long does that take?

[14:33] *silence*

[14:34] Priya: That's... a good question.

[14:35] Marco: On average? I don't know. Three to four days? If it's straightforward?

[14:36] Laura: I'd say closer to five to eight days for mine. Complex audits can take longer. Depends on the client type.

[14:37] Riccardo: And then you add however long the reporting is. So that's another day or two, sometimes more.

[14:39] Priya: So we're looking at maybe 8 to 10 days total for a complex audit, potentially?

[14:40] Marco: Yeah, that sounds about right.

[14:41] Yuki: And do you have a standard cycle-time target?

[14:42] Priya: Yes, actually. Marcus and Nora—the co-leads at Meridian—mentioned that you'd be looking at this. Our goal is to get cycle time down. The board wants us to promise clients a 3-to-5-day turnaround on standard audits. We're currently at... *gestures vaguely* ...more than that.

[14:44] Yuki: *makes note* So there's no actual data on cycle time? You're estimating?

[14:45] Marco: We've never systematically tracked it. We could, but we'd need to add timestamps to the legacy system, and honestly—

[14:46] Laura: —it's not reliable enough to trust the data anyway. The system doesn't require people to log every step. I've seen audits marked complete that I knew had work still pending.

[14:47] Yuki: So you don't have visibility into actual cycle time across the firm.

[14:48] Priya: *looks uncomfortable* No. We should. I know we should. That's something I'll take on—we need to establish cycle-time tracking from here forward. But historically, no. We've been flying blind on that metric.

[14:49] Yuki: That's actually really important data. We'll need that for any recommendations. Okay, let's talk about the legacy system itself a bit more. Marco, you mentioned it's old. How old?

[14:50] Marco: It's got to be at least eight years old now. Maybe older. We bought it off-the-shelf from some vendor that was supposed to specialize in compliance auditing. But we never customized it properly, and it turned out not to fit what we actually do.

[14:52] Laura: From what I understand, it was supposed to automate a lot of the workflow. But the automation rules were never configured correctly, so everyone just stopped using it and went back to email and spreadsheets.

[14:54] Yuki: So the system is there, but you're not really using its core features?

[14:55] Marco: Exactly. We use maybe 30% of what it offers. The status tracking, some of the client history. But everything else—the workflow engine, the assignment rules, the reporting—we've basically abandoned that and replaced it with manual processes.

[14:57] Riccardo: And it's slow. Like, just opening a client record takes 15 seconds sometimes. Running a report can time out. It's 2025 and we're using something that feels like it's from 2010. It's a constant frustration.

[14:59] Priya: We keep saying we'll replace it. But as Marco said, the license is cheap, so there's no budget pressure. And ripping it out and installing something new would require training everyone, migrating all the data...

[15:01] Marco: It would be a project. A big one.

[15:02] Yuki: *nods* I understand. We'll definitely want to map out what that transition would look like. For now, let me ask—you're maintaining parallel systems, right? Spreadsheets, email, the legacy system?

[15:03] Laura: Basically every team maintains their own spreadsheet because the legacy system is unreliable. Mine's got client names, audit types, who's assigned, where they are in the workflow, expected completion date. It's redundant with the system, but it actually works.

[15:05] Yuki: And you manually update this?

[15:06] Laura: Me or my senior consultant. Yes, manually.

[15:07] Marco: We do something similar. It's inefficient, but it's how we've adapted.

[15:08] Yuki: Okay. So process-tool fit is definitely broken. You've adapted around it instead of fixing it. That's a big finding. Now, let me shift gears. Riccardo, you mentioned reporting delays. How many reports are you producing per week?

[15:09] Riccardo: It varies. Maybe 8 to 12, depending on the month. Some are quick—maybe 2 hours of work if the audit was simple and the data exports cleanly. Others are 8 to 10 hours because of the back-and-forth with the legacy system and manual reconciliation.

[15:11] Yuki: And is the variance in time per report due to the complexity of the audit, or the system issues?

[15:12] Riccardo: Both, but honestly, more the system. A straightforward audit should take maybe 30 minutes to report if the system worked right. I'm spending 8 hours on some because I'm fighting the software.

[15:13] Marco: This is exactly what needs to change. If we could fix the reporting bottleneck, we'd get cycle time down significantly.

[15:14] Yuki: *makes note* Understood. Now, I want to circle back to something earlier. Staffing. How much turnover do you see among junior consultants?

[15:16] *silence for a moment*

[15:17] Marco: That's... a good question. More than I'd like?

[15:18] Laura: It's higher in my team than I'd prefer. People come in, work for maybe 18, 20 months, and then move on to bigger firms. They're usually good performers when they leave—they've learned the trade here, and then they get recruited away.

[15:20] Chiara: *has been quiet until now* I've seen similar. We lose people just as they're becoming truly productive.

[15:21] Yuki: Do you know what the actual turnover rate is? Annual, or over a period?

[15:22] Priya: I don't have the exact number off the top of my head. Honestly, I've been focused on the board prep this quarter and dealing with the ISO renewal we've got underway. But yes, I can pull that from HR.

[15:23] Yuki: When could you get that?

[15:24] Priya: *pauses* I've got the board prep and the ISO renewal this week, so I'm a bit swamped, but I can reach out to Giulia in HR and get the turnover data. Give me until Friday?

[15:25] Yuki: *makes note* Okay. "Priya to provide turnover data by Friday—junior consultant segment." That's important because high turnover might explain some of the cycle-time issues. You lose people right when they're productive.

[15:27] Marco: Yeah, and training a replacement sets us back.

[15:28] Yuki: Exactly. On that note—how long does it take for a new consultant to become productive? In your view?

[15:29] Marco: Full productive? Probably three weeks. They're not adding value for the first week or two—they're in training, asking questions, shadowing senior consultants.

[15:30] Laura: Mine's probably similar. Maybe closer to four weeks before they're really handling the complex audits independently. The first few weeks they're mostly doing simpler stuff—evidence gathering, documentation review. Actual audit judgment comes later.

[15:32] Yuki: And what's the board's target for this?

[15:33] Priya: Three weeks total from hire to meaningful productivity. We're currently at six weeks, so cutting it in half is the goal. It's ambitious.

[15:34] Yuki: That's a significant gap. Six weeks to three weeks. What's the bottleneck there?

[15:36] Marco: It's all of it. We don't have formalized training. People learn on the job, which is fine if they're learning from someone experienced, but that takes bandwidth from the senior consultants. And then they can't touch the systems unsupervised until they've been cleared, which can take weeks because David's IT team has to go through security protocols. Add all that up and you're at six weeks easily.

[15:38] Laura: There's also the factor that people are learning on real client work. So the learning is indirect. They're watching someone else work, asking questions, slowly absorbing methodology. If we had a structured curriculum—even just a few template audits they could practice on—it would accelerate things.

[15:40] Chiara: Agreed. And a lot of it depends on which senior consultant is training them. Some people are better teachers than others.

[15:41] Yuki: So the training is inconsistent across the firm.

[15:42] Priya: Yes. It's organic, not structured.

[15:43] Yuki: Okay, that's a clear gap we'll want to address. Now, let me ask about the queue. At any given point, how much work is sitting in the queue waiting for review?

[15:44] Laura: It varies. Right now I'd say I've got 3 or 4 pieces waiting for me. Last week it was 6. Sometimes it clears, but it fills back up.

[15:45] Marco: Similar. I usually have at least 4 or 5 sitting there. Sometimes more. That's work that's done but blocked on review.

[15:46] Yuki: And if we think about capacity—you've got four team leads, each with 4 to 6 consultants. Let's say 20 junior consultants total?

[15:47] Priya: About 22, yes.

[15:48] Yuki: So 22 junior consultants producing work, but only 4 people who can review and sign off. Is that the constraint?

[15:49] Marco: That's a big part of it. We need more capacity at the review level.

[15:50] Laura: Or we need to delegate some review authority to senior consultants who aren't team leads. But that requires more structure and documented review criteria.

[15:51] Yuki: That's a good point. You could potentially increase review capacity without hiring more team leads. But you'd need to build in controls.

[15:52] Priya: That's exactly the kind of insight we're hoping you'll help us with.

[15:53] Yuki: Understood. Now, Marco, you mentioned qualche mese fa—a few months back—you had a similar bottleneck?

[15:54] Marco: *nods* Yeah. We had a crunch about four months ago when two consultants left at the same time. We didn't replace them immediately, so we got backed up fast. The queue was five to eight days long for a couple of weeks.

[15:56] Yuki: And that was resolved by hiring?

[15:57] Priya: Eventually. But it took time to recruit and onboard. So we were understaffed for probably six weeks total.

[15:59] Yuki: And you think that's just a staffing issue, or is there something about the process or the way people are assigned work?

[16:00] Marco: The bigger issue is that we're not developing people fast enough to move them into the senior consultant role. We've got junior people who've been here for two years and are still doing junior-level work.

[16:02] Laura: *nods* That's something I've tried to fix on my team. I intentionally give people stretch assignments so they develop faster. But it's not systematic.

[16:04] Chiara: It depends on the person too. Some people are ready in 18 months. Others need three years.

[16:05] Yuki: But you don't have clear progression criteria?

[16:06] Priya: Not really. It's based on judgment.

[16:07] Yuki: That's another area where systematizing could help. You could probably accelerate progression if you had defined milestones and skill checkpoints. But I'm getting ahead of myself. Laura, you mentioned earlier that the onboarding used to be even worse?

[16:09] Laura: *nods* When I started, it was probably eight weeks. Just... nobody knew the process, there was no documentation, you were learning everything from scratch. We've made incremental improvements since then. But it's been organic, not systematic.

[16:11] Yuki: So there's been some progress, but it's been ad-hoc?

[16:12] Priya: Right. We've identified individual pain points and fixed them. Someone complained that they didn't understand the compliance framework, so we started having a Friday afternoon training session. Someone else said they needed more hands-on examples, so senior people started sharing templates. But it's not a coherent program.

[16:14] Marco: That's fair. We've kind of stumbled into an okay process, but there's no architecture to it.

[16:15] Yuki: That's actually typical at this stage. And it's fixable. The good news is you've already made progress. The challenge now is to make it deliberate.

[16:17] Riccardo: *shifts in chair* I'll say one more thing—from the reporting perspective, new people who come in don't understand the data model. They deliver audits that don't have all the information I need for clean reporting. So I end up having to go back and ask questions or dig into the source files myself. That slows down the whole cycle.

[16:19] Yuki: So there's a handoff issue between audit consultants and reporting?

[16:20] Riccardo: Exactly. There's no checklist of what needs to be in the audit for me to efficiently convert it to a report. So I get surprised by missing pieces.

[16:21] Laura: That would be something worth documenting. A reporting intake checklist.

[16:22] Yuki: *makes note* Okay, so to recap, we've got: intake inconsistency, review bottleneck, reporting delays, no cycle-time tracking, turnover data unknown, onboarding is organic not structured, and no handoff standards between audit and reporting. That's actually a really clear map of where to dig deeper.

[16:24] Priya: It's helpful to hear it all laid out. It's one thing to experience these problems individually; it's another to see the whole picture.

[16:25] Marco: Yeah. We know we've got issues, but we're usually in firefighting mode, so we don't have time to think systematically about it.

[16:26] Yuki: That's common. Okay, I think I have what I need for now. Priya, let me confirm—turnover data by Friday?

[16:27] Priya: Yeah. I'll have it.

[16:28] Yuki: Great. And we'll need to establish cycle-time tracking going forward. We can probably do that in the next phase, working with your team to instrument the system—or to set up a parallel tracking system if the legacy system isn't reliable.

[16:29] Priya: Understood.

[16:30] Yuki: Thank you. This has been really valuable. You're all doing solid work with the resources you have, and I can see where the constraints are. I'm confident there's room to improve efficiency without requiring massive new hires. We'll be back with some initial findings and a roadmap in a week or so.

[16:32] Marco: Good. Because we could definitely use some wins here.

[16:33] Laura: Agreed.

[16:34] Chiara: Thanks for digging into this.

[16:35] Riccardo: Yeah, it feels good to be heard on the reporting stuff.

[16:36] Priya: Thanks, Yuki. And keep me posted if you need anything else.

[16:37] Yuki: Will do.

[16:38] *meeting adjourns*
