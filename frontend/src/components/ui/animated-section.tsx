import { motion, type HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";

interface AnimatedSectionProps extends HTMLMotionProps<"div"> {
  delay?: number;
  className?: string;
  children: React.ReactNode;
}

export function AnimatedSection({ delay = 0, className, children, ...props }: AnimatedSectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
      className={cn(className)}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export function AnimatedFadeIn({ delay = 0, className, children, ...props }: AnimatedSectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4, delay }}
      className={cn(className)}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export function AnimatedScale({ delay = 0, className, children, ...props }: AnimatedSectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay, ease: "easeOut" }}
      className={cn(className)}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export function StaggerContainer({ className, children, ...props }: Omit<AnimatedSectionProps, 'delay'>) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: { transition: { staggerChildren: 0.08 } },
      }}
      className={cn(className)}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({ className, children, ...props }: Omit<AnimatedSectionProps, 'delay'>) {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 16 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
      }}
      className={cn(className)}
      {...props}
    >
      {children}
    </motion.div>
  );
}
