/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docsSidebar: [
    {
      type: 'category',
      label: '01. Research',
      items: [
        'research/quantum-threat-vectors',
        'research/pqc-standards',
        'research/algorithm-selection',
      ],
    },
    {
      type: 'category',
      label: '02. Deep Learning & Framework Architecture',
      items: [
        'learning/pqc-foundations',
        'learning/secure-boot-threat-model',
        'learning/mcuboot-deep-dive',
        'learning/uboot-deep-dive',
        'learning/uefi-deep-dive',
        'learning/pqc-fundamentals',
        'learning/lattice-based-crypto',
        'learning/hash-based-signatures',
      ],
    },
    {
      type: 'category',
      label: '03. Target Implementations & QEMU Verification',
      items: [
        'implementation/firmware-architecture',
        'implementation/playground',
        'implementation/hosting-guide',
        'implementation/mcuboot-pqc-integration',
        'implementation/qemu-mcuboot-verification',
        'implementation/uboot-pqc-integration',
        'implementation/uboot-qemu-verification',
        'implementation/uefi-pqc-integration',
        'implementation/uefi-qemu-verification',
      ],
    },
    {
      type: 'category',
      label: '04. Master Tutorials',
      items: [
        'tutorials/qemu-master-tutorial',
      ],
    },
    {
      type: 'category',
      label: '05. Peer Audit & Quality Consensus',
      items: [
        'audit/peer-review-consensus',
      ],
    },
    {
      type: 'category',
      label: '06. Thesis',
      items: [
        'thesis/introduction',
        'thesis/architecture-design',
        'thesis/pqc-algorithms',
        'thesis/benchmarks-analysis',
        'thesis/conclusion-future-work',
      ],
    },
    {
      type: 'category',
      label: '07. Logs & References',
      items: [
        'logs/development-logbook',
        'logs/benchmarking-results',
        'logs/qemu-execution-outputs',
      ],
    },
  ],
};

module.exports = sidebars;
