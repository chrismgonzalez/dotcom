import React from "react";
import socialStyles from "../styles/social.module.css"
import {
    faLinkedin,
    faGithub,
} from "@fortawesome/free-brands-svg-icons"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import '@fortawesome/fontawesome-svg-core/styles.css'



export default function SocialFollow() {
  return (
    <div className={socialStyles.container}>
      <a href="https://www.linkedin.com/in/cmgonzalez89/"
        className={ `${socialStyles.linkedin} ${socialStyles.social}` }>
        <FontAwesomeIcon icon={faLinkedin} size="2x" />
      </a>
      <a href="https://github.com/chrismgonzalez"
        className={`${socialStyles.github} ${socialStyles.social}`}>
        <FontAwesomeIcon icon={faGithub} size="2x" />
      </a>
    </div>
  );
}