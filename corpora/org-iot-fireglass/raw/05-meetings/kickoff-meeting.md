# Meeting Transcript: FireGlass Project Kickoff

**Date:** 2025-07-22
**Time:** 10:00 – 11:35 (CET)
**Location:** Video Call
**Attendees:** Alberto Neri (Innovative Windows LLC), Lucia Ferretti (Innovative Windows LLC), Samir Osei (Atlas Forge LLC), Clara Duval (Atlas Forge LLC)
**Facilitator:** Samir Osei
**Note-taker:** Lucia Ferretti

---

## Agenda
1. Team introductions and role clarification
2. Project vision and strategic objectives
3. Scope walkthrough — key features and deliverables
4. Authentication model and user roles
5. Argus Safety Group certification timeline and compliance requirements
6. Technology stack overview (MQTT, sensors, architecture)
7. Data migration strategy
8. Budget and sprint cadence

---

## Transcript

**Samir Osei:** Alright, great, everyone's here. Let me just start by saying it's really good to have you both on the call, Alberto and Lucia. Um, we're excited to get going on FireGlass. This is going to be a really interesting project. Before we dive into the technical details, why don't we do a quick round of introductions? I'm Samir, I'm the tech lead and product manager on our side at Atlas Forge. Clara, maybe you want to say a few words about yourself?

**Clara Duval:** Yeah, hi everyone. I'm Clara, I'm a junior developer at Atlas Forge. This is actually my first bigger project, so I'm really looking forward to working with you all. I've worked with Next.js and TypeScript in some smaller projects, so, um, yeah, excited to be here.

**Samir Osei:** Perfect. And Lucia, why don't you tell us a bit about your role?

**Lucia Ferretti:** Of course. I'm Alberto's executive assistant, so I handle a lot of the day-to-day coordination, scheduling, calendars, and I also help with documentation and internal communications. I'll be one of the users of the system, particularly for, um, administrative functions. So I'm hoping to get access to the admin dashboard when it's ready.

**Alberto Neri:** Yes, and I'm Alberto Neri, CEO of Innovative Windows LLC. We're a window manufacturing and installation company, been in the business for, let's see, about sixteen years now. But honestly, the reason we're here with you is because, um, we've realized that manufacturing and installing windows isn't really enough anymore. We're not just a window company anymore. I mean, we are, but we're becoming a tech company. That's the thing. We need to understand our products in the field, we need real-time data on installations, and we need that data to make decisions. So that's what FireGlass is about.

**Samir Osei:** Right, I love that framing. And that's actually something that came through really clearly in our conversations leading up to this. So what we're building is essentially a CRM and IoT management platform that sits on top of your existing installation workflow. It's going to let you track installations, manage customer relationships, monitor Helion sensors (TG-400 heat, SM-220 smoke, AQ-100 air quality) in real time, and pull all that data together in a way that actually informs your business decisions. Um, let me pull up the scope document that we've got here so we can walk through the main features.

**Lucia Ferretti:** Should we be taking notes? I can start recording these in the action items sheet if there are things we need to track.

**Samir Osei:** Oh, absolutely, yes, please. So, the main deliverables are: first, a customer management module. That's basically contact info, installation history, service records. Second, an installations module — you can track projects from quote to completion to warranty. Third, a sensor dashboard where you see real-time Helion data coming in from the field. Fourth, user management and roles-based access control. Fifth, data migration tools to bring in your existing installation data. And sixth, API documentation and integration guides for future extensions.

**Clara Duval:** Um, Samir, I had a question — sorry, you're not done yet, are you?

**Samir Osei:** No, go ahead.

**Clara Duval:** I was just wondering, on the sensor dashboard, do we have a sense yet of how many sensor streams we'd be processing? Because that might affect how we think about the real-time infrastructure.

**Alberto Neri:** Well, right now we have maybe, what, Lucia?

**Lucia Ferretti:** About two hundred active installations.

**Alberto Neri:** Yeah, two hundred. But that's going to grow. In the next eighteen months, I'd expect us to be at four, five hundred installations. Some of those might have multiple sensors. So, you know, the system needs to be able to scale.

**Samir Osei:** Got it. We'll definitely keep that in mind when we're designing the architecture. Now, one of the things that came up in our initial conversations is the user roles model. Alberto, you mentioned you wanted pretty granular access control, so let me walk through what we're thinking. We've got six proposed roles: Administrator, Manager, Technician, Customer Service, Read-Only Analyst, and Guest. The idea is that each role has specific permissions for what they can view and edit. Does that track with what you had in mind?

**Alberto Neri:** Um, six roles. That's... that's quite a few. Do we really need six roles? I mean, I don't want to over-complicate this. What's the use case for all of them?

**Samir Osei:** That's a fair question. So the Administrator role is basically you, or anyone you trust with system-wide access — they manage users, configure settings, that sort of thing. Manager is for your supervisors or regional leads who need to see all installations and customer data. Technician is for your field people like your installers and maintenance techs — they need to see and log data for their assigned jobs, but they shouldn't see salary information or confidential customer records. Customer Service is if you have people answering customer calls who need to look up information but not edit anything critical. The Read-Only Analyst role is for someone like a financial analyst who wants to pull data for reporting but can't make changes. And then Guest is basically, you know, limited external access if needed.

**Alberto Neri:** Okay, when you put it that way, um, I guess I see the logic. The Technician role is probably the most important one for us because we have, what, maybe thirty guys in the field?

**Lucia Ferretti:** Thirty-four as of last month.

**Alberto Neri:** Right, thirty-four. So yeah, that makes sense. Keep it.

**Samir Osei:** Great. Now, one thing that's going to be really important — you mentioned the Argus Safety Group (ASG-FP Level 2 certification) timeline in one of our earlier conversations. Can you elaborate on that a bit?

**Alberto Neri:** Yes, so, we're going through an insurance audit in November. Argus Safety Group is our underwriter, they're pretty rigorous, and ASG-FP Level 2 certification is required. They want to see documentation of our processes, our procedures, our controls. And honestly, I think having a proper system that logs all of this — installations, maintenance, incidents, data — is going to be huge for the audit. It shows we're organized, we're compliant, we're professional. So I'd like the system to be able to export compliance reports by November. That's a hard deadline for us.

**Clara Duval:** That's pretty soon. How much time are we talking from now?

**Samir Osei:** That's about sixteen weeks from today, so it fits within our timeline. We've got fifteen to seventeen weeks in the contract. But it does mean we need to make sure compliance and reporting features are solid. We'll build those in, and we should probably start thinking about what those reports need to look like pretty early on.

**Lucia Ferretti:** I can put together some sample reports from our current system — we use Excel right now — so you can see what information we're actually tracking.

**Samir Osei:** That would be really helpful. Okay, so let me talk a bit about the technology side of things. The core of the system is Next.js 14 with TypeScript for the frontend and backend API. We're using Prisma as our ORM, PostgreSQL as our database, and Supabase for some of the infrastructure. The thing that's probably most relevant to your use case is the IoT part. We're using MQTT, which is a protocol for communicating with IoT devices like your Helion sensors. The sensors connect to an MQTT broker, they publish their temperature and smoke density readings, and we consume those in real time and display them in the dashboard.

**Alberto Neri:** Okay, um, I'm going to admit right now that I don't really understand what MQTT is. Can you explain it in terms that a non-technical person would get?

**Samir Osei:** Sure. Think of it like a post office. Your sensors are like letter writers. They want to send their data somewhere. Instead of mailing it directly to the application, they send it to the MQTT broker, which is like the post office. The post office receives the message and routes it to anyone who's subscribed to that type of message. So if you have a kitchen sensor, it might publish to a "kitchen-data" topic, and any application that's subscribed to "kitchen-data" will receive that message. It's efficient, it's reliable, and it's designed for IoT scenarios where you've got lots of devices sending data all the time.

**Alberto Neri:** Okay, that makes sense. And these Helion sensors — the TG-400 and SM-220 — they come with MQTT built in, or do we have to, um, do something special to make them work with it?

**Samir Osei:** Good question. They don't come with MQTT built in, but they have a protocol called HelionLink v2.3 that's basically their proprietary way of sending data. We've got a converter that translates HelionLink into MQTT, so the system can understand it. That said, um, I do want to mention that we're waiting on some detailed documentation from Helion. Can you put me in touch with their technical team? That would be really helpful.

**Alberto Neri:** Yeah, yeah, of course. I'll connect you with their tech lead. I think his name is, uh, Lucia?

**Lucia Ferretti:** Dimitri something. I'll get you his email, Samir.

**Samir Osei:** Perfect, thank you. So, another thing I want to touch on is data migration. Clara, can you ask about the current data situation?

**Clara Duval:** Oh, um, yeah. So we'd like to understand what data you currently have and in what format. You mentioned Excel spreadsheets, Alberto, is that correct?

**Alberto Neri:** Yeah, we've got about three years of installation records in Excel. Everything from the date of the installation, the customer name, the address, the window configuration, the installer, the final sign-off. It's not perfect — some of the old records aren't as detailed as we'd like — but it's all there. We also have a spreadsheet for service calls and maintenance visits.

**Lucia Ferretti:** There are actually several spreadsheets. I can compile them and send them to you so you can see the structure.

**Samir Osei:** That would be great. We'll need to understand the schema, deal with any missing data, and then write migration scripts to bring everything into the new system cleanly.

**Alberto Neri:** How long does that typically take?

**Samir Osei:** Depends on how clean the data is and how many exceptions we find. For three years of installation records, I'd estimate a couple of sprints of work. We can build that in once the core system is stable. It's not on the critical path for the early releases.

**Alberto Neri:** Good, because I want you focused on the sensor integration and the customer dashboard. That's where the value is.

**Samir Osei:** Absolutely. Now, let's talk about sprints and cadence. We're proposing two-week sprints. At the end of each sprint, we'll do a demo on Friday where you can see what we've built, ask questions, give feedback. In between, we can do async updates or ad-hoc calls if needed. Does that work for you?

**Alberto Neri:** Friday demos — yeah, that works. Lucia, can you put that on my calendar?

**Lucia Ferretti:** Already writing it down.

**Clara Duval:** So how are we thinking about the budget? I know there's a total contract value, but is that, like, fixed-price per sprint, or...?

**Samir Osei:** It's a time-and-materials engagement. We've got a total contract value of €120,000, which covers the full fifteen to seventeen weeks. We've chunked it into sprints, and we're estimating about €7,500 per sprint. That's based on two developers, partially on this, partially on other work, so it might vary a bit sprint-to-sprint, but it should stay in that ballpark.

**Alberto Neri:** That's fine. We've got budget for this. And if there are changes to scope, we'll negotiate that separately, right?

**Samir Osei:** Exactly. If requirements change or you want to add features, we'll scope it, estimate it, and then we can either adjust the timeline or the budget. But we're aiming to keep the core deliverables within the current plan.

**Alberto Neri:** Good. I'm, um, I'm really excited about this project. You know, like I said, we need to transition from being a window company to being a company that understands its product in the field. And with real-time sensor data, compliance documentation, and customer history all in one place, I think we're going to be able to do things with our business that we can't do now. So let's build something great.

**Samir Osei:** That's the goal. We're excited too. Um, there's one more thing I want to mention. You said earlier that you need sub-second real-time streaming of sensor data. Is that accurate? Because that's a pretty aggressive requirement, and I want to make sure we understand what "real-time" means in your context.

**Alberto Neri:** Well, yeah, I mean, when a sensor detects a problem, I want to know about it immediately. Like, if there's a sudden temperature spike or smoke is detected, I don't want a thirty-second lag before the system alerts me. That defeats the purpose.

**Samir Osei:** I hear you. We'll make sure the architecture is optimized for that. With MQTT and a good broker setup, we should be able to get you pretty close to real-time — definitely sub-second for most scenarios. We'll validate that during development.

**Clara Duval:** I have a question, um, sorry. Regarding the sensor data display, are we planning to store all the raw sensor readings in the database, or just the processed ones? Because if we're getting data every sixty seconds from, you know, two hundred sensors, that's a lot of write operations.

**Samir Osei:** That's a great point. We'll probably store both — we'll have a raw MQTT payload table for forensics and debugging, but we'll also have processed, typed columns for the actual display and analysis. We can optimize the schema as we learn more about the data volume.

**Alberto Neri:** How much data are we talking about here? Like, is this going to require a big database?

**Samir Osei:** Not huge, really. Two hundred sensors, reading every sixty seconds, that's about 3,000 reads per hour per sensor metric. If we keep, say, thirty days of raw data online, we're talking maybe a few gigabytes of storage. Super manageable with Postgres.

**Lucia Ferretti:** What about reporting on that data? Will there be any bottlenecks in querying?

**Samir Osei:** Good question. We'll probably want to aggregate data for longer-term reporting — like daily or weekly averages — so that we're not scanning millions of rows every time you want to see a trend. We can set that up in Sprint 2 or 3 once we see how the data patterns actually look.

**Alberto Neri:** Alright, I think I've got a good sense of what we're building. When do you want to start?

**Samir Osei:** We can kick off Sprint 1 next Monday, July 28th. We'll use that sprint to set up the development environment, build the basic data models, get the database schema in place, and start work on the authentication and user management system. By the end of that sprint, you'll have a working login page and a basic dashboard template.

**Alberto Neri:** Perfect. Lucia, make sure you're looped in on all the updates. And I'll get you that introduction to Helion. Anything else, Samir?

**Samir Osei:** I think we're good. We'll send over a detailed project plan and the technical specification before Sprint 1 starts. And Clara will set up a Slack channel so we can communicate between these calls. Sound good?

**Alberto Neri:** Sounds great. Let's do this.

---

## Action Items
- [ ] **Alberto Neri**: Introduce Samir to Helion technical lead for HelionLink documentation — Due: 2025-07-25
- [ ] **Lucia Ferretti**: Compile and send all historical installation data spreadsheets to Atlas Forge — Due: 2025-07-25
- [ ] **Lucia Ferretti**: Add Friday sprint demos to Alberto's calendar (recurring, 2-week cadence starting 2025-08-01) — Due: 2025-07-23
- [ ] **Samir Osei**: Send detailed project plan and technical specification document — Due: 2025-07-25
- [ ] **Clara Duval**: Create Slack workspace and send invites to all attendees — Due: 2025-07-24
- [ ] **Samir Osei**: Set up development environment and PostgreSQL schema for Sprint 1 — Due: 2025-07-28

## Decisions Made
- Six-role access control model approved (Administrator, Manager, Technician, Customer Service, Read-Only Analyst, Guest)
- Two-week sprint cadence with Friday demos confirmed
- Sprint budget: €7,500 per sprint (subject to variance)
- Argus Safety Group compliance reporting as hard requirement, must be ready by November 2025
- Real-time sensor data display target: sub-second latency
- Data migration from Excel to database to begin in Sprint 2-3 (not critical path)
- Project starts Monday, July 28th, 2025
