<template>
  <div id="discover-container">
    <div id="pages">
      <ul>
        <li :class="{ active: page == 'how-it-works' }" @click="changePage('how-it-works')">
          <span>How it works</span>
        </li>
        <li :class="{ active: page == 'giving-lessons' }" @click="changePage('giving-lessons')">
          <span>Giving lessons</span>
        </li>
        <li :class="{ active: page == 'taking-lessons' }" @click="changePage('taking-lessons')">
          <span>Taking lessons</span>
        </li>
        <li :class="{ active: page == 'faq' }" @click="changePage('faq')">
          <span>FAQ</span>
        </li>
        <li :class="{ active: page == 'friends' }" @click="changePage('friends')">
          <span>Information for testers</span>
        </li>
      </ul>
    </div>
    <div id="page-container">
      <div class="page" v-show="page == 'how-it-works'">
        <h2>How it works</h2>
        <p>Tutortime is an online timebanking platform focused on learning.</p>
        <p>
          Each user starts with a default set of minutes for their account. You can book a lesson with any tutor in a
          subject you are interested in. Once the lesson has completed, the duration (in minutes) of the lesson is
          deducted from your account and added to your tutor's account. For you to earn minutes you will need to become
          the tutor and teach another student in a subject you are familiar with.
        </p>
        <p>
          You don't need to be an expert to help other student's learn! Check out our post on
          <RouterLink :to="{ path: 'discover', query: { page: 'giving-lessons' } }">Giving lessons</RouterLink> for more
          details on how to give a lesson, and tips to help you out.
        </p>
        <h2>Our values</h2>
        <p>On Tutortime, we want to build a community where:</p>
        <ul>
          <li>members help each other learn and grow as individuals</li>
          <li>relationships are fostered outside a monetary system</li>
          <li>everyone in the community has value and has something to contribute</li>
        </ul>
      </div>
      <div class="page" v-show="page == 'giving-lessons'">
        <h2>Giving lessons</h2>
        <p>
          In order to earn minutes on tutortime you will need to give lessons to other members. You can start by
          clicking on <RouterLink to="/user/services">Give lessons</RouterLink> on the top bar. There you will be able
          to create new services.
        </p>
        <p>
          A service describes a subject that you are comfortable teaching to others. Services that you create will be
          viewable by other members who will message you if they want to book a lesson with you.
        </p>

        <h2>Which subjects should I teach?</h2>
        <p>
          You do not need to be an expert in a subject in order to teach it; you just need to be able to help your
          student's progress in their learning. To do this you will need to first evaluate your knowledge level.
        </p>
        <p>
          For subjects that are taught in school this should be relatively easy to figure out. If you did well in a
          particular subject, like grade 12 chemistry, then you should be capable of tutoring a student taking that same
          course (assuming it's the same curriculum).
        </p>
        <p>
          For subjects normally outside of school, like sewing, this might be slightly trickier and you will need to
          make a judgement call based on what you know about yourself, and what your students are asking of you. You can
          ask yourself the following questions:
        </p>
        <ul>
          <li>How many months / years have I been learning this subject?</li>
          <li>What particular techniques am I familiar with?</li>
          <li>When's the last time I practiced?</li>
        </ul>
        <p>
          When creating a service, ensure that your description clearly describes how comfortable you are in that
          subject area. This will help you and your students align with eachother before starting a lesson.
        </p>

        <h2>Tips on giving lessons</h2>
        <ol>
          <li>Choose a subject that you enjoy(ed) learning about</li>
          <li>Ensure your service description clearly outlines how comfortable you are in that subject</li>
          <li>
            Prior to booking a lesson with a student, figure out their expectations. Have a plan in mind for what will
            be covered in the lesson
          </li>
        </ol>
      </div>
      <div class="page" v-show="page == 'taking-lessons'">
        <h2>Taking lessons</h2>
        <p>
          In order to take lessons on tutortime you need some minutes saved up. You can see your balance by checking
          your <RouterLink to="/user/profile">Profile</RouterLink> or on the right-side of a
          <RouterLink to="/chat">Chat</RouterLink>. Each user begins with a default of 60 minutes. After those have been
          used, they will need to offer lessons to other students to earn more minutes.
        </p>
        <p>
          Since tutortime operates outside a traditional educational system, where curriculum and learning objectives
          are clearly outlined, there is a greater onus on students to figure out what they want to learn and whether
          their tutor is capable of helping them.
          <b>Students should not expect their tutors to dictate everything.</b> They need to take some initiative in
          coming up with a plan for the lesson.
        </p>

        <h2>Tips on taking lessons</h2>
        <ul>
          <li>Think about what subject you need help with, and any learning objectives you have</li>
          <li>Browse the <RouterLink to="/">Take lessons</RouterLink> page to find the current offerings</li>
          <li>
            Send a message to a suitable tutor
            <ul>
              <li>Explain why you are interested in the subject they teach</li>
              <li>Describe your current skill level and any learning objectives you have</li>
            </ul>
          </li>
          <li>Figure out a date / time to meet with your tutor</li>
          <li>Have a plan in mind for what you would like to cover in the lesson</li>
        </ul>
      </div>
      <div class="page" v-show="page == 'faq'">
        <h3>What is time-based currency? What is a timebank?</h3>
        <p>
          A <a href="https://en.wikipedia.org/wiki/Time-based_currency" target="_blank">time-based currency</a> is a
          currency system that uses a person's time as it's unit of measurement rather than dollars. Community members
          use their time to help other members and in return they are given a credit. They can redeem these credits by
          getting another member of the community to help them.
        </p>
        <p>
          A timebank is a platform that tracks the time exchanges between members and maintains the accurate account
          balances. This is analagous to how a traditional bank tracks dollars between different banks accounts.
        </p>

        <h3>What is tutortime?</h3>
        <p>
          Tutortime is a timebank that is focused on helping people learn new skills and subjects. Tutors on the
          platform can volunteer their time to help a student with a subject they are familiar with. In return, they are
          awarded Tutortime <i>minutes</i> which they can then use towards a tutoring session (i.e. a lesson) in a
          subject they are interested in.
        </p>
        <p>
          Since Tutortime is a closed system, where you can only earn minutes by teaching other students, it relies
          solely on it's members and their ability to teach eachother.
        </p>

        <h3>How much is a minute worth?</h3>
        <p>
          The basic unit of measurement on Tutortime is a minute. For each minute you spend teaching another student you
          will be rewarded a minute on the platform. You can then redeem these minutes to learn from a tutor on
          Tutortime.
        </p>
        <p>
          Tutortime values everyone's time equally; regardless of what you teach and who you teach you will earn 1
          minute on the platform for every minute spent tutoring.
        </p>

        <h3>Can I exchange minutes for dollars or vise-versa?</h3>
        <p>
          Tutortime does not allow for minutes to be exchanged for dollars, or vise-versa. It is a closed system where
          you can only earn credits by teaching other students, and you can only spend credits by learning from other
          students.
        </p>

        <h3>How do I earn minutes?</h3>
        <p>
          You can earn minutes by teaching a lesson. Check out
          <RouterLink :to="{ path: 'discover', query: { page: 'giving-lessons' } }">Taking lessons</RouterLink> for more
          details.
        </p>

        <h3>Am I able to have a negative balance?</h3>
        <p>
          You are not able to book a lesson unless you have sufficient minutes to do so. Only in rare circumstances will
          your balance enter the negative.
        </p>
      </div>
      <div class="page" v-show="page == 'friends'">
        <h3>Hello friends</h3>
        <p>Thank you for taking the time to visit my site.</p>
        <p>
          I started working on this idea in my free time back in August 2023. The site was initially developed using
          Python and Flask, as these were the frameworks comfortable to me at the time. After about 9 months of work I
          built a site with functionality similar to what you will see today. However I decided to abondon that code
          base as it was not very maintainable and the site itself would not scale well (i.e. if more users joined the
          platform I would need to spend more and more money on infrastructure because my code was not very performant).
        </p>
        <p>
          I ended up rewriting the entire code base using Golang and VueJS. These frameworks were new to me when I
          started, however I understood that they would make my site more performant and therefore cheaper to run
          (something that I care about if this site is going to be run off donations). I also thought that the struggle
          of learning a new language and web development framework to build the site was more aligned with the ethos of
          the platform; not taking the familiar path but instead putting in the effort to learn something new. What you
          see today is the product of that effort, and indeed it still has a very long way to go. The code thus far is
          available on <a href="https://github.com/mikey-boy/tutortime" target="_blank">Github</a>
          if you are interested.
        </p>

        <h3>Testing</h3>
        <p>
          I encourage you to play around with the site. Create local accounts, create as many of them as you like. Try
          creating a service, try messaging someone, try <RouterLink to="/services/1">booking a lesson</RouterLink>.
          Click on all the buttons and see if their functionality is intuitive or not. Once you've gotten a feel for the
          site, I would really appreciate any feedback you may have. You can provide this to me by either filling out
          this
          <a
            href="https://docs.google.com/forms/d/e/1FAIpQLSfzewlad-ehZ07IGUa_lV2jSPNpypUz2HV2trnZzvpChKFNwQ/viewform?usp=sf_link"
            target="_blank"
            >Google Form</a
          >
          or just sending me a text.
        </p>
        <p>
          Thank you again for visiting the site :) A good place to start is probably the
          <RouterLink :to="{ path: 'discover', query: { page: 'how-it-works' } }">How it works</RouterLink> page and
          then you can just explore from there!
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      page: this.$route.query.page || "how-it-works",
    };
  },
  methods: {
    changePage(page) {
      this.page = page || "how-it-works";
      this.$router.push({ path: `/discover`, query: { page: page } });
    },
  },
  watch: {
    $route: function (val, oldVal) {
      this.changePage(this.$route.query.page);
    },
  },
};
</script>

<style>
#discover-container {
  display: flex;
  margin: 0 auto;
  max-width: 1100px;
  font-size: 19px;
}
#pages {
  flex: 2;
  margin: 60px 60px 0px 0px;

  ul {
    list-style: none;
    padding: 0;
    border: 2px solid var(--green0);
    border-radius: 3px;
  }
  li {
    cursor: pointer;
    color: var(--text0);
    text-align: center;
    border-radius: 3px;
    padding: 8px;
    &:hover {
      background-color: var(--base1);
    }
  }
  li.active {
    background-color: var(--base1);
  }
}
#page-container {
  flex: 12;

  .page {
  }
}
</style>
