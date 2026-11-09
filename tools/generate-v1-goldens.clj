;; Regenerates validation/text/{clipboard,client-log}/golden.edn by running
;; v1's own parsers (the oracle) over the recorded inputs.
;;
;; Run from PowerShell in the v1 repository (conda is NOT needed; these
;; parsers are pure and this script refuses to run if capture or Python
;; namespaces get loaded):
;;
;;   Set-Location C:\Users\JB\git\indite-cortex
;;   $env:INDITE_FIXTURES = "C:\Users\JB\git\indite-cortex-fixtures"
;;   clojure -M:dev -i C:\Users\JB\git\indite-cortex-fixtures\tools\generate-v1-goldens.clj
;;
;; It starts only v1's in-memory db state (mount/start #'db/server-db_), as
;; v1's own craft test fixtures do; it binds no ports. Datamine-derived
;; fields (:id, :item-type) depend on v1's local RePoE reference files.

;; Scratch: produce v1 golden outputs for validation/text. Loaded with
;;   clojure -M:dev -i golden_v1.clj   (from v1's directory). Writes only into the fixtures repo.
(require '[clojure.java.io :as io]
         '[clojure.pprint :as pp]
         '[clojure.string :as str])

(require '[indite-cortex.model.poe.log.parse :as log-parse]
         '[indite-cortex.model.poe.log.events :as log-events])
(require '[mount.core :as mount]
         '[indite-cortex.db.server :as db]
         '[indite-cortex.model.poe.data.item :as item])

(def forbidden '[indite-cortex.capture.monitor indite-cortex.config.python])
(println "forbidden namespaces loaded:" (filterv find-ns forbidden))
(when (some find-ns forbidden)
  (println "STOP: parser transitively loads capture.monitor/config.python")
  (System/exit 2))

;; Only the in-memory server-db atom state (no ports, no other components) -- the same
;; scoped start v1's own craft-fixtures/fresh-db! uses.
(mount/start #'db/server-db_)

(def fx (str (or (System/getenv "INDITE_FIXTURES") "../indite-cortex-fixtures") "/validation/text/"))

(defn parse-clipboard [raw]
  (let [lines (item/generate-raw-item-data raw)]
    (get-in (item/parse-raw-item-data {:craft/target {:target/raw lines}})
            [:craft/target :target/parse])))

(defn write-edn [f v]
  (with-open [w (io/writer f :encoding "UTF-8")]
    (binding [*out* w *print-namespace-maps* false pp/*print-right-margin* 100]
      (pp/pprint v))))

(def clip-files (->> (.listFiles (io/file fx "clipboard"))
                     (filter #(str/ends-with? (.getName %) ".txt"))
                     (sort-by #(.getName %))))

(def clip-golden
  (mapv (fn [f]
          (let [raw (String. (java.nio.file.Files/readAllBytes (.toPath f)) "UTF-8")
                out (parse-clipboard raw)]
            (println (.getName f) "->" (if (map? out) (vec (sort (keys out))) out)
                     "chars:" (count (pr-str out)))
            {:input (.getName f) :output out}))
        clip-files))

(def log-lines (str/split-lines (slurp (io/file fx "client-log" "lines.txt") :encoding "UTF-8")))

(def log-golden
  (mapv (fn [line]
          {:line line
           :output {:envelope (log-parse/parse-envelope line)
                    :event (log-parse/parse-line log-events/event-defs line)}})
        log-lines))

(write-edn (io/file fx "clipboard" "golden.edn") clip-golden)
(write-edn (io/file fx "client-log" "golden.edn") log-golden)
(println "wrote" (count clip-golden) "clipboard goldens," (count log-golden) "log goldens")
(shutdown-agents)
(System/exit 0)
