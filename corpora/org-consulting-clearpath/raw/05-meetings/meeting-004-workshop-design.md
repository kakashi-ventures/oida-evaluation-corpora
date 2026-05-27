# Meeting 004: Implementation Workshop
**Date:** October 28, 2025
**Location:** ClearPath Solutions Inc., Florence office, Conference Room B
**Attendees:** Marcus Webb (Lead, Meridian Labs), Nora Chen (Co-lead, Meridian Labs), Yuki Tanaka (Analyst, Meridian Labs), Priya Anand (Head of Operations, ClearPath), David Park (CTO, ClearPath), Marco Fiore (Team Lead, ClearPath), Riccardo Boni (Team Lead, ClearPath), Chiara Lentini (Quality Assurance Lead, ClearPath)
**Duration:** 120 minutes (14:00–16:00)

---

[14:00] Marcus: So the goal of this workshop is to work through the implementation approach for the recommendations. We're going to dive into specific processes—onboarding, the audit queue, system access provisioning—and design what the revised approach should look like. This isn't the final decision-making meeting. This is where we get into the details and make sure we understand what's feasible and what the tradeoffs are.

[14:02] Nora: We'll move through three key areas. First the audit review process, then onboarding, then we'll tackle system access. Sound good?

[14:03] Marcus: Right. Let's start with audit review. The current state is serial review—junior consultant completes the audit, it goes into a queue, a senior person reviews it, it's done. The bottleneck is the senior person review capacity. One approach is parallel review—structured peer review plus spot-check supervision. Another is to restructure the audit itself—do more upfront validation so the review is lighter. David, Marco, what's your instinct on this?

*[14:05] A knock on the conference room door. Chiara enters, apologizing quietly.*

[14:05] Chiara: Sorry, sorry. Got held up. I'm here now.

[14:06] Marcus: No problem. Chiara, we were just starting on the audit review bottleneck. We're exploring whether we restructure the review process or change how the audits are conducted upfront.

[14:08] David: I think the audit process itself is doing too much. We could split the compliance check from the documentation check. Get the quick stuff validated upfront, flag the complex items for deeper review.

[14:10] Marco: Okay, but the clients don't always distinguish. They send a file, and we need to validate everything. I mean, we could change the workflow on our side, but the input from the client side is what it is.

[14:12] Riccardo: I think David's onto something. We could process the files in two passes. First pass is preliminary validation—make sure there's no obvious gaps or errors. Then a second pass is detailed review, but the preliminary pass can happen faster.

[14:14] David: Exactly. And the second pass can be lighter if we've already filtered out the easy stuff.

[14:16] Marco: But who does the first pass? Are we asking junior consultants to do a preliminary review, and then asking them again for the full review? That seems like double work.

[14:18] Nora: Actually, no. The first pass is a different person potentially. The idea is: junior consultant completes initial audit—this is preliminary. It gets marked. Then it goes to either a peer for initial validation, or to a checklist-based process where we're just checking box items. Then the senior review is a true review of nuance and judgment, not of obviously correct items.

[14:20] David: Right. Which reduces the review time.

[14:22] Marco: I mean, I hear what you're saying, but in practice... *pauses* ...the junior consultants are going to feel like they're not being trusted. Right now they do the audit, and we review it. If we add a preliminary check step, are we saying their work isn't good enough?

[14:24] Priya: That's a fair psychological concern.

[14:25] Chiara: Could we frame it as a tiered review system? Like, tier one is the preliminary pass, tier two is senior review. That way it's not about trust, it's about—

[14:27] David: It's still checking the work twice.

[14:28] Riccardo: But it could be framed differently. Instead of "we're checking your work again," it's "we're validating before we escalate to the senior reviewer." It's part of the process, not a reflection on competence.

[14:30] Marcus: Let me reframe. This isn't about whether the current approach is bad. It's about whether there's a more efficient way to do the same job. And yes, Marco, the change management piece is critical. But that's a separate conversation. For now, let's assume people can understand the rationale and adapt. Does the process make sense from a pure workflow standpoint?

[14:32] Marco: From a pure workflow standpoint, yes. It probably saves a day or two on the queue.

[14:34] Nora: Okay. Let's call that option A. We can also explore option B, which is to hire another senior reviewer and keep the current process. But that's a cost versus process conversation, and we want to understand the process possibilities first.

[14:36] David: I'd rather change the process. We're not hiring people well right now anyway.

[14:37] Priya: That's a bit unfair. We've had some good hires recently.

[14:38] David: A few. But the turnover is still significant.

[14:40] Chiara: Actually, I've been thinking about this from a QA perspective. Before summer we tried something similar—a peer-review pilot—where we had junior people validate each other's work before escalating to senior review.

[14:42] Marco: And?

[14:43] Chiara: And it didn't stick. Culturally, people didn't trust the peer review. They still wanted the senior person to do the full check. So we abandoned it after four weeks.

[14:45] Marco: There we go. That's what I'm talking about. Culturally, it doesn't work.

[14:47] Nora: But that was a pilot. It didn't have proper framing. If we announce this as a structural change, with clear rationale, it might land differently.

[14:49] Chiara: Maybe. But I'm just saying we've tried a version of this before, and the resistance was real.

[14:51] David: The resistance would be different if it came from leadership as a designed process, not as a quick pilot.

[14:53] Riccardo: I agree. The framing matters.

[14:55] Marcus: So what we're hearing is: the process could work, but change management is critical. Is that fair?

[14:57] Nora: I think we need to decide today whether we're actually pursuing this approach or not. Are we going with the tiered review system, or are we looking at hiring another senior person?

[14:59] Marco: I don't know. Both have problems. The tiered system has culture problems, hiring has capacity problems and—

[15:01] Priya: *phone buzzes. She glances at it, frowns.* Sorry, give me one second. *She stands, apologizing.* I'm so sorry. We have a client emergency. I need to take this. I'll be back in five minutes.

[15:02] Marcus: Of course. Go ahead.

*[15:03] Priya leaves the room. There's a brief pause.*

[15:03] Chiara: This happens every meeting, doesn't it?

[15:04] Riccardo: At least twice a week.

[15:05] Marco: It's one of the reasons onboarding gets de-prioritized, honestly. Whenever something urgent comes up, everything else gets shelved.

[15:07] David: There's no escalation protocol. It's just whoever knows about it tries to fix it.

[15:09] Nora: That's something we should flag. But for now, let's keep moving. Let's talk about onboarding while we wait. Riccardo, you've been doing some work on standardizing the curriculum, right?

[15:11] Riccardo: Yeah. I've built a structured onboarding path for my team. New people work through a checklist, they pair with an assigned mentor for the first week, and then they do supervised audits for the second week. It's tighter.

[15:13] Marcus: How long does that take to full autonomy?

[15:14] Riccardo: About four weeks. Three weeks to be pretty functional.

[15:15] Nora: So you're closer to the target already?

[15:16] Riccardo: Yeah. Because I made the curriculum explicit.

[15:18] Marco: The issue is the curriculum takes time to develop, and Riccardo's been here longer, so he's got more experience to draw from.

[15:20] David: You could copy his curriculum.

[15:21] Marco: I could. But it needs to be adapted to my team's client base. We handle different types of files.

[15:23] Riccardo: Not that different. There's overlap.

[15:25] Chiara: The risk with copying directly is that we'll lose institutional knowledge. Like, Riccardo's curriculum works for Riccardo's team because he understands the nuances of how his clients work.

[15:27] Riccardo: But the core pieces are transferable.

[15:29] Priya: *returns* What did I miss?

[15:30] Marcus: We're talking about standardizing the onboarding curriculum. Riccardo's built something that's working for his team, and we're discussing whether it's scalable.

[15:32] Priya: Okay. I'm back. Sorry. File format issue with a client—easy fix, but they needed it escalated.

[15:34] Nora: Is this something that needs a process change on your side?

[15:35] Priya: Maybe. We'll see.

[15:37] Nora: So, onboarding. I think what we need to decide is: do we have a firm-wide curriculum, or does each team develop their own?

[15:39] Marco: I think it's somewhere in the middle. Core curriculum that everyone learns, then team adaptations.

[15:41] Riccardo: That's what I was thinking.

[15:43] Chiara: But who maintains the core curriculum? Who decides what's in it?

[15:45] Marcus: That's a good question. Let's table that for a second. Does everyone agree that standardization is the right direction?

[15:47] Marco: In principle, yes.

[15:48] Riccardo: Yes.

[15:49] Priya: Yes.

[15:50] Chiara: I think so, but I'd want to see what it looks like before I commit to it.

[15:52] Nora: Okay. So action item: Riccardo works with Marco and Chiara—and we'd want Laura too—to create a standardized curriculum framework. Timeframe?

[15:54] Marco: Two weeks? I'd want to integrate it with the next hire.

[15:55] Riccardo: Two weeks is tight but reasonable.

[15:57] Chiara: I can contribute. I have ideas about what should be in QA onboarding.

[15:59] Marcus: Great. Two weeks. We'll check in after that.

[16:01] Nora: Now, system access. David, why does it take so long?

*[16:02] There's a rustling of papers. Someone drops a pen.*

[16:02] Marcus: Sorry, is someone on a call?

[16:03] Chiara: No, that was me. Clumsy.

[16:04] David: System access takes longer than it should. The process is: someone creates a ticket, I route it to our access management system, it goes through a few approvals, and then we provision. It's three to five days typically.

[16:06] Priya: But new hires sometimes sit waiting for a week or more.

[16:08] David: That's not the access provisioning part. That's the waiting for someone to create the ticket. Or sometimes the security review takes longer. But the actual provisioning itself?

[16:10] Nora: So there are delays upstream and downstream of the actual provisioning process?

[16:12] David: Yeah.

[16:14] Marco: Can we shorten those?

[16:15] David: The upstream is Priya's side—someone needs to notify me that a new person is starting. We could automate that.

[16:17] Priya: We should be doing that. I think it's just... sometimes it falls through the cracks when people are juggling a lot.

[16:19] David: The downstream is security review. That's... *long pause* ...that's not something I can promise to expedite. There are compliance rules around who can access what.

[16:21] Marcus: But you could flag which accesses need security review upfront, right? So when someone sends the request, it's pre-vetted in terms of security?

[16:23] David: Maybe. But before summer we tried something similar, and it didn't really help. The bottleneck is still the security approval itself.

[16:25] Chiara: I'm not familiar with that. What did you try?

[16:26] David: It was... a pre-screening process. Supposed to make the formal review faster. Didn't work out.

[16:28] Riccardo: Could you have a standing approval person? Someone who's designated to do those reviews on a schedule?

[16:30] David: Possibly. But that's me. And I've got a lot on my plate.

[16:32] Priya: David, this is a priority. If it's you, we can look at your backlog and see what else can be moved.

[16:34] David: Okay. I'll think about it.

[16:36] Nora: So action item: David evaluates whether dedicated time to access provisioning security reviews is feasible, and what the impact would be. When can you get back to us?

[16:38] David: Uh... maybe next week?

[16:39] Priya: David, you're going to be slammed next week. How about you give us a preliminary take by Friday, and we circle back?

[16:41] David: Yeah, okay. Friday.

[16:43] *[16:43] David glances at his watch.*

[16:43] David: Actually, I have another call at 15:30, so I'm going to need to head out in about five minutes. Can we wrap on this?

[16:45] Marcus: We're basically done. We still need to touch on reporting templates.

[16:47] David: Okay. Well, that's not my area, so I can probably go.

[16:48] Nora: Wait, David. Before you go—when can we circle back on the access provisioning? We need to know your timeline.

[16:50] David: Like I said, Friday for the preliminary take.

[16:51] Nora: And then when for a full discussion?

[16:52] David: Tuesday? Wednesday? I don't know yet. Send me a calendar invite and I'll accept.

[16:54] David: *stands and gathers his things* I'll check on the security review situation. Talk soon.

*[16:55] David leaves the room.*

[16:56] Priya: Okay. So we're down to reporting templates. Marco?

[16:57] Marco: Right. I wanted to talk about the templates we use for client reporting. The current state is that each team has their own, and there's no consistency. Clients see different formats depending on which team they're working with.

[16:59] Chiara: How much does that matter?

[17:00] Marco: It matters for how professional we look. And it matters internally—if there's no standard, then when someone moves between teams, they have to learn a new template system.

[17:02] Riccardo: My team uses a version that's... pretty detailed. Other teams might be lighter.

[17:04] Marco: Exactly. So we could standardize. Have a firm-wide template, maybe with team-level customization for specific client types.

[17:06] Nora: Is this something that's blocking efficiency, or is it more of a quality thing?

[17:08] Marco: It's a quality thing. And, I mean, consistency is a quality thing. But it's not a bottleneck like audit review or onboarding.

[17:10] Chiara: But it's worth fixing. I've noticed inconsistencies when I'm doing QA spot checks across teams.

[17:12] Marcus: So is this something we should include in the recommendations, or is it a separate effort?

[17:14] Nora: I think we can include it as a recommendation. But in terms of design and implementation, is that something you want to tackle in this workshop?

[17:16] Marco: Not necessarily. I just wanted to flag it.

[17:18] Riccardo: We could say: "Standardize reporting templates as a separate workstream. Riccardo and Marco develop a baseline, other teams provide input."

[17:20] Marco: That could work.

[17:22] Chiara: How long would that take?

[17:23] Marco: I don't know. Four weeks? Six weeks? Depends on how much customization teams want.

[17:25] Riccardo: It's not a fast thing, no.

[17:27] Nora: Okay. So we're looking at onboarding curriculum in two weeks, access provisioning evaluation by Friday, audit review process design in a week, and then reporting templates as a longer-term effort.

[17:29] Marcus: That's a lot. But I think those are the priorities. Let me see if I'm missing anything.

[17:31] Priya: I think those are the main ones. The client emergency thing we flagged—that's something we can look at internally.

[17:33] Chiara: I want to come back to the audit review process. I'm still not convinced the tiered system will work. We tried peer review before and it didn't stick.

[17:35] Marco: Right. So what are the alternatives?

[17:37] David: *already gone*

[17:38] Marcus: Well, the other option is to hire another senior reviewer. But that's a cost conversation.

[17:40] Chiara: I'm not arguing against tiered review. I'm just saying we need to be realistic about the culture piece. If we do this, we need executive sponsorship. People need to hear from leadership that this is the way forward, not a workaround.

[17:42] Nora: That's fair. But that's the change management piece that we said is separate from the design.

[17:44] Chiara: Is it separate, though? If the culture won't support it, then the design doesn't matter.

[17:46] Riccardo: But we won't know if the culture will support it until we try.

[17:48] Chiara: We already did try. We know it didn't work before.

[17:50] Marco: But this would be different. It's not a pilot. It's a designed system with clear rationale.

[17:52] Chiara: Maybe. But I'm going to stay skeptical.

[17:54] Nora: Okay. So the action item is: we design out the tiered review system, and then as part of change management, we address the cultural concerns. Does that work?

[17:56] Chiara: I guess. But I'm flagging that this might not work.

[17:58] Marcus: Flagged. And we'll include that in the recommendations.

[18:00] Priya: When are we reconvening to discuss this?

[18:02] Nora: Tuesday, I think. David said Tuesday.

[18:03] Marcus: Let's say Tuesday. I'll send a summary and we can regroup then.

[18:05] Nora: Can we at least agree on what we discussed today? Like, do we have consensus that these are the right priorities?

[18:07] Riccardo: The audit review, onboarding, and access provisioning—yes.

[18:08] Marco: Yeah. Though I'm still not sold on the tiered review.

[18:10] Nora: You said it makes sense from a workflow perspective.

[18:11] Marco: It does. But I'm worried about the culture piece.

[18:13] Marcus: So we're not in consensus. We're in "let's explore and see what the design looks like."

[18:15] Priya: That's fine for now. We can make a real decision once we have the design.

[18:17] Chiara: But when will that be? How much time do people have to do this?

[18:19] Riccardo: I can dedicate time. I was thinking maybe I do the design work, and people give input.

[18:21] Chiara: Do you have a week for that?

[18:22] Riccardo: I'll make it work.

[18:24] Marcus: So the action item is: Riccardo designs out the tiered audit review system with input from the team. One week. Then we review and discuss on Tuesday.

[18:26] Nora: And David evaluates access provisioning by Friday.

[18:27] Marco: And the onboarding curriculum framework in two weeks.

[18:29] Priya: So we have staggered deadlines.

[18:30] Marcus: Yes. We'll get the access provisioning input first, then the audit review, then we'll wait for the onboarding framework.

[18:32] Nora: Okay. I think we need to wrap. Can we just confirm: Tuesday we reconvene?

[18:34] Priya: Not Monday, Monday is packed.

[18:36] Marcus: Tuesday then. We'll send a summary of what we discussed.

[18:38] Nora: What, exactly, did we decide today?

[18:40] *[Long pause]*

[18:41] Marcus: We... discussed the options. We identified that tiered review could work but has change management implications. We identified that onboarding standardization is the direction. And we identified that access provisioning needs both upstream and downstream fixes.

[18:43] Nora: But we didn't decide on any of those things.

[18:45] Riccardo: We decided we'd design out the tiered review system and see what it looks like.

[18:47] Chiara: Which might not work.

[18:48] Priya: We can decide when we see the design.

[18:50] Nora: Okay. So what's the actual next step here?

[18:52] Marcus: Riccardo designs. David evaluates. We regroup Tuesday.

[18:54] Marco: And in the meantime, we all think about our concerns?

[18:56] Marcus: Sure. That's helpful.

[18:58] Nora: I feel like we're going in circles.

[19:00] Priya: We've covered a lot of ground though. We've identified the options, the tradeoffs, the concerns.

[19:02] Marcus: That's true. And we have action items.

[19:04] Chiara: Vague action items.

[19:06] Marcus: They're not vague. Riccardo designs. David evaluates. We reconvene Tuesday.

[19:08] Nora: Okay. Let me just summarize so we're all clear. We're going to design out the tiered audit review system, possibly recognizing it might have culture problems. We're going to develop a standardized onboarding curriculum framework. We're going to have David evaluate dedicated time for access provisioning security reviews. And we're going to flag the reporting templates standardization as a longer-term effort. Is that right?

[19:11] Marco: Yes.

[19:12] Riccardo: Yes.

[19:13] Priya: Yes.

[19:14] Chiara: Yes, but with caveats.

[19:16] Marcus: I think we've covered a lot of ground today. Let me synthesize the discussion and we can reconvene.

[19:18] Riccardo: When?

[19:19] Priya: Tuesday. But not early. My day is packed in the morning.

[19:21] Nora: Same. Afternoon would be better.

[19:23] Marcus: Let's say Tuesday, 14:00. Same room.

[19:25] Priya: I'll add it to my calendar.

[19:27] Marcus: I'll send a summary of the action items and the options we discussed. Everyone review it before Tuesday.

[19:29] Nora: *quietly, to herself* A summary of what, exactly?

[19:31] Riccardo: Sorry?

[19:32] Nora: Nothing. I just... we'll see Tuesday.

[19:34] *[19:34] Brief silence.*

[19:35] Chiara: This was good. I think. At least we all know what the options are.

[19:37] Marco: That's something.

[19:39] *[Meeting adjourns. People gather their things slowly. Conversation continues informally but without clear resolution.]*
