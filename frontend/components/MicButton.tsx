import { useLocalParticipant } from "@livekit/components-react";
import React from "react";
import { FaMicrophone, FaMicrophoneSlash } from "react-icons/fa";
import { motion } from "framer-motion";

export function MicButton() {
    const { isMicrophoneEnabled, localParticipant } = useLocalParticipant();

    const toggleMic = () => {
        if (localParticipant) {
            localParticipant.setMicrophoneEnabled(!isMicrophoneEnabled);
        }
    };

    return (
        <motion.button
            whileTap={{ scale: 0.9 }}
            whileHover={{ scale: 1.05 }}
            onClick={toggleMic}
            className={`
          relative z-10 flex items-center justify-center w-20 h-20 rounded-full shadow-2xl transition-all border-4 
          ${!isMicrophoneEnabled ? "bg-slate-700 border-slate-600" : "bg-gradient-to-br from-blue-500 to-indigo-600 border-blue-300 shadow-blue-500/50"}
        `}
        >
            {isMicrophoneEnabled ? (
                <FaMicrophone className="w-8 h-8 text-white" />
            ) : (
                <FaMicrophoneSlash className="w-8 h-8 text-slate-400" />
            )}
        </motion.button>
    );
}
