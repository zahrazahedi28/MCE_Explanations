(define (problem prob) 
(:domain blocksworld)
(:objects d b a c)
(:init (clear c) (clear a) (clear b) (clear d) (ontable c) (ontable a)
(ontable b) (ontable d) (handempty))
(:goal (and (on d c) (on c b) (on b a))))
